# cython: language_level=3str, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True
# , linetrace=True
try:
    import cython
    from cython import int as cint
except ImportError:
    print("Warning! import use fake cython!")
    from ._fake_cython import Cython

    cython = Cython()

    cint = cython.int

from typing import Union, Tuple, List, Dict


NUM_ENCODING: str = cython.declare(str, "ascii")
VAL_ENCODING: str = cython.declare(str, "utf-8")

TypeEncodable = Union[str, int, List, set, Tuple, Dict, bytes, bytearray, bool]

if not cython.compiled:
    print("Warning! bencode not compiled!")


@cython.cfunc
@cython.inline
def _bencode_set(value: set, r: "cython.list"):
    r.append(b"l")
    for k in value:
        _bencode(k, r)
    r.append(b"e")


@cython.cfunc
@cython.inline
def _bencode_int(value: int, r: "cython.list"):
    r.append(b"i")
    r.append(str(value).encode(NUM_ENCODING))
    r.append(b"e")


@cython.cfunc
@cython.inline
def _bencode_bytes(value: bytes, r: "cython.list"):
    r.append(str(len(value)).encode(NUM_ENCODING))
    r.append(b":")
    r.append(value)


@cython.cfunc
@cython.inline
def _bencode_dict(value: dict, r: "cython.list"):
    i: cython.Py_ssize_t
    key: str | bytes
    keys: cython.list = sorted(value)
    r.append(b"d")
    for i in range(len(keys)):
        key = keys[i]
        if isinstance(key, str):
            _bencode_bytes(key.encode(VAL_ENCODING), r)
        else:
            _bencode_bytes(key, r)
        _bencode(value[key], r)
    r.append(b"e")


@cython.cfunc
@cython.inline
def _bencode_list(value: list | tuple, r: "cython.list"):
    i: cython.Py_ssize_t
    r.append(b"l")
    for i in range(len(value)):
        _bencode(value[i], r)
    r.append(b"e")


@cython.cfunc
@cython.inline
def _bencode(value: TypeEncodable, r: "cython.list"):
    if isinstance(value, (bytes, bytearray)):
        _bencode_bytes(value, r)

    elif isinstance(value, int):
        _bencode_int(value, r)

    elif isinstance(value, dict):
        _bencode_dict(value, r)

    elif isinstance(value, (list, tuple)):
        _bencode_list(value, r)

    elif isinstance(value, str):
        _bencode_bytes(value.encode(VAL_ENCODING), r)

    elif isinstance(value, set):
        _bencode_set(value, r)

    elif isinstance(value, bool):
        _bencode_int(int(value), r)
    else:
        raise ValueError(f"Unable to encode `{type(value)}` {value}")


@cython.ccall
def bencode(value: TypeEncodable) -> bytes:
    r: cython.list[bytes] = []
    _bencode(value, r)
    return b"".join(r)


@cython.nogil
@cython.cfunc
@cython.inline
def _parse_forward(till_char: cython.char, encoded: cython.p_char, pos: cint) -> Tuple[cint, cint]:
    idx: cint = pos + 1
    number: cint = 0
    ichar: cython.char = encoded[pos]
    if ichar == 45:  # '-' 负值
        while True:
            ichar = encoded[idx]
            idx += 1
            if ichar == till_char:
                break
            number = number * 10 - (ichar - 48)
    else:
        number = ichar - 48
        while True:
            ichar = encoded[idx]
            idx += 1
            if ichar == till_char:
                break
            number = number * 10 + (ichar - 48)

    return number, idx


@cython.cfunc
@cython.inline
def _bdecode_list(encoded: cython.p_char, pos: cint, ilist: "cython.list") -> cint:
    ichar: cython.char = encoded[pos]
    number: cint = 0
    while True:
        if 47 < ichar < 58:  # 0-9 bytes
            # 0:48 1:49 2:50 3:51 4:52 5:53 6:54 7:55 8:56 9:57 ::58
            number, pos = _parse_forward(58, encoded, pos)  #:
            ilist.append(encoded[pos : pos + number])
            pos += number

        elif ichar == 105:  # i Integer
            number, pos = _parse_forward(101, encoded, pos + 1)  # e
            ilist.append(number)

        elif ichar == 101:
            return pos + 1

        elif ichar == 100:  # d Dictionary
            iidict: dict = {}
            pos = _bdecode_dict(encoded, pos + 1, iidict)
            ilist.append(iidict)

        elif ichar == 108:  # l List
            iilist: cython.list = []
            pos = _bdecode_list(encoded, pos + 1, iilist)
            ilist.append(iilist)

        else:
            raise ValueError(f"Unable to interpret `{chr(ichar)}`:{ichar} char.")

        ichar = encoded[pos]


@cython.cfunc
@cython.inline
def _bdecode_dict(encoded: cython.p_char, pos: cint, idict: dict) -> cint:
    ichar: cython.char = encoded[pos]
    number: cint = 0
    key: bytes
    while True:
        # 0:48 1:49 2:50 3:51 4:52 5:53 6:54 7:55 8:56 9:57 ::58
        number, pos = _parse_forward(58, encoded, pos)  #:
        key = encoded[pos : pos + number]
        pos += number

        ichar = encoded[pos]

        if 47 < ichar < 58:  # 0-9 bytes
            # 0:48 1:49 2:50 3:51 4:52 5:53 6:54 7:55 8:56 9:57 ::58
            number, pos = _parse_forward(58, encoded, pos)  #:
            idict[key] = encoded[pos : pos + number]
            pos += number

        elif ichar == 105:  # i Integer
            number, pos = _parse_forward(101, encoded, pos + 1)  # e
            idict[key] = number

        elif ichar == 108:  # l List
            iilist: cython.list = []
            pos = _bdecode_list(encoded, pos + 1, iilist)
            idict[key] = iilist

        elif ichar == 100:  # d Dictionary
            iidict: dict = {}
            pos = _bdecode_dict(encoded, pos + 1, iidict)
            idict[key] = iidict

        else:
            raise ValueError(f"Unable to interpret `{chr(ichar)}`:{ichar} char.")

        ichar = encoded[pos]

        if ichar == 101:
            return pos + 1


@cython.ccall
def bdecode(encoded: cython.p_char):
    """Decodes bencoded data introduced as bytes.

    Returns decoded structure(s).

    :param encoded:

    """

    number: cint
    ichar: cython.char = encoded[0]

    if ichar == 100:  # d Dictionary
        idict: dict = {}
        _bdecode_dict(encoded, 1, idict)
        return idict

    elif ichar == 108:  # l List
        ilist: cython.list = []
        _bdecode_list(encoded, 1, ilist)
        return ilist

    elif 47 < ichar < 58:  # 0-9 bytes
        # 0:48 1:49 2:50 3:51 4:52 5:53 6:54 7:55 8:56 9:57 ::58
        pos: cint
        number, pos = _parse_forward(58, encoded, 0)  #:
        return encoded[pos : pos + number]

    elif ichar == 105:  # i Integer
        number, _ = _parse_forward(101, encoded, 1)  # e
        return number

    else:
        raise ValueError(f"Unable to interpret `{chr(ichar)}`:{ichar} char.")
