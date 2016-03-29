# -*- coding: utf-8 -*-
class StructFieldDescriptor:
    """Generic descriptor type for defining a formatted struct field"""
    fmt = typ = ctype = None
    size = 0

    def __init__(self, name=None, count=1, sizeof=None, byte_order=None):
        self.name, self.count, self.sizeof = name, count, sizeof
        self.byte_order = byte_order
        self.val = None

        # if we have a callback to determine our size, then set a default size
        # of 1 so we can rely on our count to determine how many bytes we're
        # unpacking
        if self.sizeof is not None and self.size is 0:
            self.size = 1

    def __get__(self, instance, instance_type):
        return self.val

    def __set__(self, instance, val):
        self.val = val

    def __mul__(self, other):
        return self.__class__(self.name, self.format, self.size*other, self.typ)
    __imul__ = __rmul__ = __mul__

    def __str__(self):
        return '<%s> %d' % (self.ctype, self.size)
    __repr__ = __str__

    @property
    def format(self):
        return '%d%s' % (self.count, self.fmt)


class PadByteField(StructFieldDescriptor):
    """A padding byte. Does not map to a specific Python type and is
    effectively thrown away once parsed
    """
    fmt = 'x'
    typ = type(None)
    ctype = 'pad byte'


class CharField(StructFieldDescriptor):
    """A single C char type. Will be loaded as a bytes object of length 1"""
    fmt = 'c'
    typ = bytes
    size = 1
    ctype = 'char'


class SignedCharField(StructFieldDescriptor):
    """A signed C char type. Will be loaded as an integer value"""
    fmt = 'b'
    typ = int
    size = 1
    ctype = 'signed char'


class UnsignedCharField(SignedCharField):
    """An unsigned C char type. Will be loaded as an integer value"""
    fmt = 'B'
    ctype = 'unsigned char'


class BooleanField(StructFieldDescriptor):
    """The _Bool type defined by C99. If this type is not available on the
    current system, then it will be simulated using a char. In standard mode,
    it is always represented as a single byte
    """
    fmt = '?'
    typ = bool
    size = 1
    ctype = '_Bool'


class ShortField(StructFieldDescriptor):
    fmt = 'h'
    typ = int
    size = 2
    ctype = 'short'


class UnsignedShortField(ShortField):
    fmt = 'H'
    ctype = 'unsigned short'


class IntegerField(StructFieldDescriptor):
    fmt = 'i'
    typ = int
    size = 4
    ctype = 'int'


class UnsignedIntegerField(IntegerField):
    fmt = 'I'
    ctype = 'unsigned int'


class LongField(IntegerField):
    fmt = 'l'
    ctype = 'long'


class UnsignedLongField(LongField):
    fmt = 'L'
    ctype = 'unsigned long'


class LongLongField(LongField):
    fmt = 'q'
    size = 8
    ctype = 'long long'


class UnsignedLongLongField(LongLongField):
    fmt = 'Q'
    ctype = 'unsigned long long'


class SSizeTField(StructFieldDescriptor):
    fmt = 'n'
    typ = int
    size = 8
    ctype = 'ssize_t'


class SSizeTField(SSizeTField):
    fmt = 'N'
    ctype = 'size_t'


class FloatField(StructFieldDescriptor):
    fmt = 'f'
    typ = float
    size = 4
    ctype = 'float'


class DoubleField(StructFieldDescriptor):
    fmt = 'd'
    typ = float
    size = 8
    ctype = 'double'


class CharArrayField(StructFieldDescriptor):
    fmt = 's'
    typ = bytes
    ctype = 'char[]'

    def __init__(self, name=None, count=1, sizeof=None, encoding=None):
        super(self.__class__, self).__init__(name, count, sizeof)
        self.encoding = encoding


class CharArrayField2(CharArrayField):
    fmt = 'p'
    ctype = 'char[]'


class VoidPointerField(StructFieldDescriptor):
    fmt = 'P'
    ctype = 'void *'
