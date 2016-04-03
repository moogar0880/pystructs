# -*- coding: utf-8 -*-
"""Utility functions for the Struct API module"""


def safe_decode(string, encoding='utf-8'):
    """attempt to decode the provided data string using the specified encoding.
    if a decode error occurs, just return the provided byte string
    """
    try:
        return string.decode(encoding)
    except UnicodeDecodeError:
        return string


class StatefulByteStream:
    """A :const:`bytes` type wrapper which maintains stateful information about
    how much of the provided bytestream has already been read through
    """

    def __init__(self, stream):
        """Create a new StatefulByteStream instance

        :param stream: A :const:`bytes` object to maintain the state of
        """
        self.data = stream
        self.offset = 0

    def slice(self, size, start=0):
        """Return a slice of this Byte stream

        :param size: The size of the slice to cut
        :param start: The start index (relative to the current position in this
            bytestream) to create the slice from
        """
        to_ret = self.data[self.offset+start:self.offset+size]
        self.offset += size
        return to_ret

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return self.data.__len__()

    def __str__(self):
        return self.data.__str__()

    def __bytes__(self):
        return self.data

    def __eq__(self, other):
        return self.data.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    __repr__ = __str__
