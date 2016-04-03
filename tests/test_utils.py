# -*- coding: utf-8 -*-
from pystructs.utils import StatefulByteStream, safe_decode


def test_statefulbytestream():
    """test the functionality of the StatefulByteStream class"""
    data = b'\x00\x00\x00\x01'
    bs = StatefulByteStream(data)
    assert bs.offset == 0
    assert len(bs) == len(data)
    assert str(bs) == str(data)
    assert bytes(bs) == data
    assert bs == data
    assert bs != bs[::-1]
    assert repr(bs) == str(bs)
    assert bs.slice(2) == data[0:2]
    assert bs.offset == 2


def test_safedecode():
    """test that safe_decode will decode byte strings, only if it can"""
    data = [
        (b'safe',          'safe'),
        (b'\x00\x03\xb0*', b'\x00\x03\xb0*'),
    ]

    for inp, expected in data:
        assert safe_decode(inp) == expected
