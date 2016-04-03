# -*- coding: utf-8 -*-
class StructFieldDescriptor:
    """Generic descriptor type for defining a formatted struct field"""
    _fmt = _typ = _ctype = None
    _size = 0

    def __init__(self, name=None, count=1, sizeof=None, byte_order=None):
        """Create a new struct field descriptor instance

        :param name: The name of this descriptor as it will appear in it's
            containing class type
        :param count: The count of this field descriptor's size to unpack
            from the provided binary data
        :param sizeof: A callback used to dynamically determine the count of
            this field descriptor to unpack
        :param byte_order: An optionally specified byte_order specification for
            use in scenarios where, for instance, a little-endian number is
            stored inside of a big-endian data stream
        """
        self._name, self._count, self._sizeof = name, count, sizeof
        self._byte_order = byte_order
        self._val = None

        # if we have a callback to determine our size, then set a default size
        # of 1 so we can rely on our count to determine how many bytes we're
        # unpacking
        if self._sizeof is not None and self._size == 0:
            self._size = 1

    def __get__(self, instance, instance_type):
        return self._val

    def __set__(self, instance, val):
        self._val = val

    def __mul__(self, other):
        return self.__class__(self._name, self._format, self._size*other, self._typ)
    __imul__ = __rmul__ = __mul__

    def __str__(self):
        return '<%s> %s' % (self._ctype, str(self._size))
    __repr__ = __str__

    @property
    def _format(self):
        return '%d%s' % (self._count, self._fmt)


class PadByteField(StructFieldDescriptor):
    """A padding byte. Does not map to a specific Python type and is
    effectively thrown away once parsed
    """
    _fmt = 'x'
    _typ = type(None)
    _ctype = 'pad byte'


class CharField(StructFieldDescriptor):
    """A single C char type. Will be loaded as a bytes object of length 1"""
    _fmt = 'c'
    _typ = bytes
    _size = 1
    _ctype = 'char'


class SignedCharField(StructFieldDescriptor):
    """A signed C char type. Will be loaded as an integer value"""
    _fmt = 'b'
    _typ = int
    _size = 1
    _ctype = 'signed char'


class UnsignedCharField(SignedCharField):
    """An unsigned C char type. Will be loaded as an integer value"""
    _fmt = 'B'
    _ctype = 'unsigned char'


class BooleanField(StructFieldDescriptor):
    """The _Bool type defined by C99. If this type is not available on the
    current system, then it will be simulated using a char. In standard mode,
    it is always represented as a single byte
    """
    _fmt = '?'
    _typ = bool
    _size = 1
    _ctype = '_Bool'


class ShortField(StructFieldDescriptor):
    _fmt = 'h'
    _typ = int
    _size = 2
    _ctype = 'short'


class UnsignedShortField(ShortField):
    _fmt = 'H'
    _ctype = 'unsigned short'


class IntegerField(StructFieldDescriptor):
    _fmt = 'i'
    _typ = int
    _size = 4
    _ctype = 'int'


class UnsignedIntegerField(IntegerField):
    _fmt = 'I'
    _ctype = 'unsigned int'


class LongField(IntegerField):
    _fmt = 'l'
    _ctype = 'long'


class UnsignedLongField(LongField):
    _fmt = 'L'
    _ctype = 'unsigned long'


class LongLongField(LongField):
    _fmt = 'q'
    _size = 8
    _ctype = 'long long'


class UnsignedLongLongField(LongLongField):
    _fmt = 'Q'
    _ctype = 'unsigned long long'


class SSizeTField(StructFieldDescriptor):
    _fmt = 'n'
    _typ = int
    _size = 8
    _ctype = 'ssize_t'


class SSizeTField(SSizeTField):
    _fmt = 'N'
    _ctype = 'size_t'


class FloatField(StructFieldDescriptor):
    _fmt = 'f'
    _typ = float
    _size = 4
    _ctype = 'float'


class DoubleField(StructFieldDescriptor):
    _fmt = 'd'
    _typ = float
    _size = 8
    _ctype = 'double'


class CharArrayField(StructFieldDescriptor):
    _fmt = 's'
    _typ = bytes
    _ctype = 'char[]'

    def __init__(self, name=None, count=1, sizeof=None, encoding=None):
        """

        :param length: The length of each char array to unpack
        """
        super(self.__class__, self).__init__(name, count, sizeof)
        self._encoding = encoding


class CharArrayField2(CharArrayField):
    _fmt = 'p'
    _ctype = 'char[]'


class VoidPointerField(StructFieldDescriptor):
    _fmt = 'P'
    _ctype = 'void *'


class ArrayField(StructFieldDescriptor):
    """The ArrayField is a non-standard field used to describe a series of data
    which encapsulates a series of other field types
    """
    _typ = list

    def __init__(self, base_field, name=None, count=None, sizeof=None, **kwargs):
        """Create a new ArrayField descriptor

        :param base_field: A base :class:`StructFieldDescriptor` used when
            unpacking individual segments of binary data
        :param name: The name of this descriptor as it will appear in it's
            containing class type
        :param count: The count of an array field is a callback used to
            determine the number of array items to unpack
        :param sizeof: A callback used to dynamically determine the size of the
            binary data stream slice to unpack
        :param kwargs: Any additional keyword arguments to provided to
            `base_field` when it's created to unpack array items
        """
        self._base_field = base_field
        self._kwargs = kwargs
        super(self.__class__, self).__init__(name, count, sizeof)

    @property
    def _fmt(self):
        """alias to _base_field's _fmt"""
        return self._base_field._fmt

    @property
    def _ctype(self):
        """alias to _base_field's _ctype"""
        return self._base_field._ctype

    @property
    def _size(self):
        """_size aliased to _base_field's size, or 1 if our base field doesn't
        have a size
        """
        return self._base_field._size or 1

    def __len__(self):
        if self._val is None:
            return 0
        return len(self._val)
