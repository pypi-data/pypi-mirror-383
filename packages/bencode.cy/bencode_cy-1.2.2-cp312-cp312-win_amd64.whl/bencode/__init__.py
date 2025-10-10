try:
    from ._bencodec import bencode, bdecode, TypeEncodable

    compiled = True
except ImportError:
    from ._bencode import bencode, _bencode, TypeEncodable

    compiled = False
