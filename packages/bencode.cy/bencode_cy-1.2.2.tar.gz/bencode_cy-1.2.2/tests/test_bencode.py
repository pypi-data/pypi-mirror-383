import pytest
import sys
from pathlib import Path

from bencode import bencode, bdecode


@pytest.fixture
def tor():
    f = Path("tests/debian-mac-13.1.0-amd64-netinst.iso.torrent")
    return f.read_bytes()


def test_bencode():
    assert bencode("WWWWWW") == b"6:WWWWWW"
    assert bencode(233) == b"i233e"
    assert bencode(-1) == b"i-1e"


def test_bdecode():
    assert bdecode(b"6:WWWWWW") == b"WWWWWW"
    assert bdecode(b"i233e") == 233
    assert bdecode(b"i-123e") == -123


def test_bdecode_dict():
    e1 = b"d6:WWWWWW6:WWWWWWe"
    print(bdecode(e1))
    assert bencode(bdecode(e1)) == e1


def test_bdecode_list():
    e1 = b"l6:WWWWWW6:WWWWWWe"
    print(bdecode(e1))
    assert bencode(bdecode(e1)) == e1


def test_torrent_py(tor):
    from bencode._bencode import bdecode, bencode

    torrent = bdecode(tor)
    print(torrent[b"creation date"])
    assert torrent[b"announce"] == b"http://bttracker.debian.org:6969/announce"
    print(bencode(torrent)[:160])
    print(tor[:160])
    assert tor == bencode(torrent)


def test_torrent(tor):
    torrent = bdecode(tor)
    assert torrent[b"announce"] == b"http://bttracker.debian.org:6969/announce"
    assert tor == bencode(torrent)


@pytest.mark.benchmark()
def test_bdecode_benchmark(benchmark, tor):
    benchmark.name = "bencode.cy.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_bencode_benchmark(benchmark, tor):
    benchmark.name = "bencode.cy.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_bdecode_py_benchmark(benchmark, tor):
    from bencode._bencode import bdecode

    benchmark.name = "bencode.cy.decodepy"

    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_bencode_py_benchmark(benchmark, tor):
    from bencode._bencode import bdecode, bencode

    benchmark.name = "bencode.cy.encodepy"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
@pytest.mark.skipif(sys.version_info >= (3, 12), reason="anything")
def test_bdecoder_pyx_benchmark(benchmark, tor):
    from bencoder import bdecode, bencode

    benchmark.name = "bencoder.pyx.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
@pytest.mark.skipif(sys.version_info >= (3, 12), reason="anything")
def test_bencoder_pyx_benchmark(benchmark, tor):
    from bencoder import bdecode, bencode

    benchmark.name = "bencoder.pyx.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_fastdecode_rust_benchmark(benchmark, tor):
    from fastbencode import bdecode, bencode

    benchmark.name = "fastbencode.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_fastbencode_rust_benchmark(benchmark, tor):
    from fastbencode import bdecode, bencode

    benchmark.name = "fastbencode.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_bdecodepy_benchmark(benchmark, tor):
    from bencodepy import decode as bdecode

    benchmark.name = "bencodepy.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_bencodepy_benchmark(benchmark, tor):
    from bencodepy import decode as bdecode
    from bencodepy import encode as bencode

    benchmark.name = "bencodepy.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_better_bdecode_benchmark(benchmark, tor):
    from better_bencode import loads as bdecode

    benchmark.name = "better_bencode.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_better_bencode_benchmark(benchmark, tor):
    from better_bencode import loads as bdecode
    from better_bencode import dumps as bencode

    benchmark.name = "better_bencode.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_bdecoding_benchmark(benchmark, tor):
    from bcoding import bdecode, bencode

    benchmark.name = "bcoding.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_bencoding_benchmark(benchmark, tor):
    from bcoding import bdecode, bencode

    benchmark.name = "bcoding.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
@pytest.mark.skipif(sys.version_info <= (3, 13), reason="anything")
def test_bdecode_rs_benchmark(benchmark, tor):
    from bencode_rs import bdecode, bencode

    benchmark.name = "bencode_rs.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
@pytest.mark.skipif(sys.version_info <= (3, 13), reason="anything")
def test_bencode_rs_benchmark(benchmark, tor):
    from bencode_rs import bdecode, bencode

    benchmark.name = "bencode_rs.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)


@pytest.mark.benchmark
def test_bdecode2_benchmark(benchmark, tor):
    from bencode2 import bdecode, bencode

    benchmark.name = "bencode2.decode"
    benchmark(bdecode, tor)


@pytest.mark.benchmark
def test_bencode2_benchmark(benchmark, tor):
    from bencode2 import bdecode, bencode

    benchmark.name = "bencode2.encode"
    e2 = bdecode(tor)
    benchmark(bencode, e2)
