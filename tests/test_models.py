# -*- coding: utf-8 -*-
from pystructs import fields
from pystructs.models import StructObject, NativeByteOrder


def test_simple_object():
    """test a simple class type with a single field to be unpacked"""
    data = b'\x00\x00\x00\x01'
    class Sized(StructObject):
        size = fields.IntegerField()

    s = Sized()
    s.unpack(data)
    assert s.size == 1
    assert s.pack() == data
    assert s.ctype == Sized.__qualname__


def test_count_field():
    """test a simple class type with multiple field types and a count variable
    set
    """
    data = b'\x00\x01\x00\x02\x00\x00\x00\x03'
    class Example(StructObject):
        shorts = fields.ShortField(count=2)
        long_data = fields.LongField()

    ex = Example()
    ex.unpack(data)
    assert ex.shorts == (1, 2)
    assert ex.long_data == 3
    assert ex.pack() == data
    assert ex.ctype == Example.__qualname__


def test_nested():
    """test a nested struct object and ensure that the data can be successfully
    packed and unpacked
    """
    class Sub(StructObject):
        foo = fields.IntegerField()

    class Container(StructObject):
        bar = fields.ShortField()
        nested = Sub()
    data = b'\x00\x01\x00\x00\x00\x01'

    container = Container()
    container.unpack(data)

    assert container.bar == 1
    assert isinstance(container.nested, Sub)
    assert container.nested.foo == 1
    assert container.pack() == data


def test_dependant():
    """test that a dynamically sized field can be packed an unpacked using the
    `sizeof` paramater
    """
    class VariableLengthString(StructObject):
        length = fields.IntegerField()
        string_data = fields.CharArrayField(encoding='utf-8',
                                            sizeof=lambda x: x.length)

    data = b'\x00\x00\x00\x06foobar'

    vls = VariableLengthString()
    vls.unpack(data)

    assert vls.length == 6
    assert vls.string_data == 'foobar'
    assert vls.pack() == data


def test_override_byte_order():
    class MyData(StructObject):
        length = fields.IntegerField()
        char = fields.UnsignedCharField(byte_order=NativeByteOrder)

    data = b'\x00\x00\x00\x06\x0c'
    d = MyData()
    d.unpack(data)

    assert d.length == 6
    assert d.char == 12
    assert d.pack() == data
