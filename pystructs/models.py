# -*- coding: utf-8 -*-
"""Data model objects for the Structs API"""
import logging
import struct
from collections import OrderedDict, Iterable
from pystructs.fields import StructFieldDescriptor, ArrayField
from pystructs.utils import StatefulByteStream, safe_decode

NativeByteOrder = '@'
StandardNativeByteOrder = '='
LittleEndianByteOrder = '<'
BigEndianByteOrder = '>'
NetworkByteOrder = '!'


class StructObjectMeta(type):
    """Metaclass for flagging the descriptors of implementing classes"""

    @classmethod
    def __prepare__(cls, name, bases):
        """Use an :const:`OrderedDict` to prepare the subclass's class dict
        with in order to preserve the order in which the fields were described.
        This ensures that the class representation of structured binary data
        can unpack correctly
        """
        return OrderedDict()

    def __new__(cls, clsname, bases, clsdict):
        """Map the attribute name to the name of the corresponding descriptor
        instances and store all descriptor names in a _fields attribute for
        faster inspections
        """
        fields = [key for key, val in clsdict.items()
                  if isinstance(val, StructFieldDescriptor)]

        # enable inheriting our parent class's struct fields, if they're present
        for base in bases:
            if issubclass(base, StructFieldDescriptor) and hasattr(base, '_fields'):
                for field in base._fields:
                    field_obj = base.__dict__[field]
                    clsdict[field_obj._name] = field_obj
                fields.extend(base._fields)

        for name in fields:
            clsdict[name]._name = name
        clsdict['_fields'] = fields

        return super().__new__(cls, clsname, bases, dict(clsdict))


class StructObject(StructFieldDescriptor, metaclass=StructObjectMeta):
    """Base class for class representations of structured binary data"""
    #: Byte Ordering scheme to use for this class's binary data. Default is
    #: :const:`NetworkByteOrder`
    BYTE_ORDER = NetworkByteOrder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def __fields(self):
        """Dynamic accessors which returns access to all field descriptors"""
        return [self.__class__.__dict__[f] for f in self.__class__._fields]

    @property
    def _size(self):
        return sum(f._size for f in self.__fields)

    @property
    def _ctype(self):
        return self.__class__.__qualname__

    @property
    def _format(self):
        return ''.join(f._format for f in self.__fields)

    def _unpack_sizeof(self, field, stream):
        """handle unpacking a :class:`StructFieldDescriptor` that has a sizeof
        callback

        :param field: The :class:`StructFieldDescriptor` to unpack
        :param stream: A :const:`bytes` object to extract data from
        """
        field._count = field._sizeof(self)
        self.logger.info('unpacking sizeof field %s (%s) as %s', str(field._name), str(field), field._format)
        field._val = struct.unpack(
            self.BYTE_ORDER + field._format,
            stream.slice(field._size*field._count)
        )
        # for char[] types, unless the encoding is set to None, decode
        # the field._val tuple using the specified encoding
        if field._typ is bytes and field._encoding is not None:
            field._val = safe_decode(field._val[0], field._encoding)

    def _unpack_array(self, field, stream):
        """Unpack and ArrayField into a list of it's base_field types"""
        _count = field._count(self)
        _size = int(field._sizeof(self) / _count)
        fmt_size = int(_size / (field._base_field._size or 1))
        field._val = [
            struct.unpack(self.BYTE_ORDER + '%d%s' % (fmt_size, field._fmt),
                          stream.slice(_size))
            for _ in range(_count)
        ]

        typed_values = []
        for f in field._val:
            base = field._base_field(**field._kwargs)
            base._val = f
            if base._typ is bytes and base._encoding is not None:
                base._val = [safe_decode(val, base._encoding)
                             for val in base._val]
            else:
                field._val = [val for val in base._val]
            typed_values.extend(base._val)
        field._val = typed_values


    def unpack(self, stream):
        """unpack the provided binary data stream into this class's fields

        :param stream: A :const:`bytes` object to extract data from
        :return: The :class:`StructObject` object unpacked from the provided
            :const:`bytes` `stream`
        """
        if not isinstance(stream, StatefulByteStream):
            stream = StatefulByteStream(stream)
            self.logger.info('unpacking stream of size %d', len(stream))

        # map unpacked values to the fields that they correspond to
        for field in self.__fields:
            # self.logger.info('unpacking field %s (%s) as %s', str(field._name), str(field), field._format)
            if isinstance(field, StructObject):
                field._val, stream = field.unpack(stream)
            elif isinstance(field, ArrayField):
                self._unpack_array(field, stream)
            elif field._sizeof is not None:
                self._unpack_sizeof(field, stream)
            else:
                fmt = (field._byte_order or self.BYTE_ORDER) + field._format
                slice_size = field._size * field._count
                field._val = struct.unpack(fmt, stream.slice(slice_size))

            # if we unpacked something that was not a collection or a byte
            # string, remove the single element from it's containing tuple
            if field._count == 1 and field._typ is not bytes and isinstance(field._val, tuple):
                field._val = field._val[0]

        # return the current instance from unpack to facilitate chaining
        # :class:`StructObject` instances
        return self, stream

    def pack(self):
        """Return this class as a :const:`bytes` representation of this
        :class:`StructObject`

        :return: The packed :const:`bytes` representation of this
            :class:`StructObject`
        """
        output = b''
        for field in self.__fields:
            order = field._byte_order or self.BYTE_ORDER
            if isinstance(field._val, StructObject):
                output += struct.pack(
                    order + field._format,
                    *[f._val for f in field.__fields]
                )
            elif isinstance(field, ArrayField):
                output += struct.pack(
                    order + '%d%s' % (len(field), field._fmt),
                    *field._val
                )
            elif isinstance(field._val, str):
                output += struct.pack(
                    order + field._format,
                    bytes(field._val, field._encoding or 'utf-8')
                )
            elif isinstance(field._val, Iterable) and not isinstance(field._val, bytes):
                output += struct.pack(
                    order + field._format,
                    *field._val
                )
            else:
                output += struct.pack(
                    order + field._format,
                    field._val
                )
        return output
