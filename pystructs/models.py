# -*- coding: utf-8 -*-
"""Data model objects for the Structs API"""
import logging
import struct
from collections import OrderedDict, Iterable
from pystructs.fields import StructFieldDescriptor
from pystructs.utils import StatefulByteStream

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
        for name in fields:
            clsdict[name].name = name
        clsdict['_fields'] = fields

        return super().__new__(cls, clsname, bases, dict(clsdict))


class StructObject(StructFieldDescriptor, metaclass=StructObjectMeta):
    """Base class for class representations of structured binary data"""
    #: Byte Ordering scheme to use for this class's binary data. Default is
    #: :const:`NetworkByteOrder`
    BYTE_ORDER = NetworkByteOrder

    @property
    def __fields(self):
        """Dynamic accessors which returns access to all field descriptors"""
        return [self.__class__.__dict__[f] for f in self.__class__._fields]

    @property
    def size(self):
        return sum(f.size for f in self.__fields)

    @property
    def ctype(self):
        return self.__class__.__qualname__

    @property
    def format(self):
        return ''.join(f.format for f in self.__fields)

    def _unpack_sizeof(self, field, stream):
        """handle unpacking a :class:`StructFieldDescriptor` that has a sizeof
        callback

        :param field: The :class:`StructFieldDescriptor` to unpack
        :param stream: A :const:`bytes` object to extract data from
        """
        field.count = field.sizeof(self)
        field.val = struct.unpack(
            self.BYTE_ORDER + field.format,
            stream.slice(field.size*field.count)
        )
        # for char[] types, unless the encoding is set to None, decode
        # the field.val tuple using the specified encoding
        if field.typ is bytes and field.encoding is not None:
            field.val = field.val[0].decode(field.encoding)

    def unpack(self, stream):
        """unpack the provided binary data stream into this class's fields

        :param stream: A :const:`bytes` object to extract data from
        :return: The :class:`StructObject` object unpacked from the provided
            :const:`bytes` `stream`
        """
        if not isinstance(stream, StatefulByteStream):
            stream = StatefulByteStream(stream)

        # map unpacked values to the fields that they correspond to
        for field in self.__fields:
            fmt = (field.byte_order or self.BYTE_ORDER) + field.format
            slice_size = field.size * field.count
            if isinstance(field, StructObject):
                field.val = field.unpack(stream.slice(slice_size))
            elif field.sizeof is not None:
                self._unpack_sizeof(field, stream)
            else:
                field.val = struct.unpack(fmt, stream.slice(slice_size))

            # if we unpacked something that was not a collection or a byte
            # string, remove the single element from it's containing tuple
            if field.count == 1 and field.typ is not bytes and isinstance(field.val, tuple):
                field.val = field.val[0]

        # return the current instance from unpack to facilitate chaining
        # :class:`StructObject` instances
        return self

    def pack(self):
        """Return this class as a :const:`bytes` representation of this
        :class:`StructObject`

        :return: The packed :const:`bytes` representation of this
            :class:`StructObject`
        """
        output = b''
        for field in self.__fields:
            if isinstance(field.val, StructObject):
                output += struct.pack(
                    (field.byte_order or self.BYTE_ORDER) + field.format,
                    *[f.val for f in field.__fields]
                )
            elif isinstance(field.val, str):
                output += struct.pack(
                    (field.byte_order or self.BYTE_ORDER) + field.format,
                    bytes(field.val, field.encoding or 'utf-8')
                )
            elif isinstance(field.val, Iterable) and not isinstance(field.val, bytes):
                output += struct.pack(
                    (field.byte_order or self.BYTE_ORDER) + field.format,
                    *field.val
                )
            else:
                output += struct.pack(
                    (field.byte_order or self.BYTE_ORDER) + field.format,
                    field.val
                )
        return output
