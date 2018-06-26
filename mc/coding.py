import struct


__all__ = ['Decoder', 'Encoder']


class BufferTooShort(Exception):
    pass


class Decoder:
    def __init__(self, buf):
        self.buf, self.pos = buf, 0

    def peek(self, offset):
        if len(self.buf) - self.pos <= offset:
            raise BufferTooShort

        return ord(self.buf[self.pos + offset])

    def _unpack(self, fmt):
        size = struct.calcsize(fmt)
        if len(self.buf) - self.pos < size:
            raise BufferTooShort

        items = struct.unpack_from('<' + fmt, self.buf, self.pos)
        self.pos += size
        if len(items) == 1:
            return items[0]
        else:
            return items

    def unsigned_byte(self):
        return self._unpack('B')

    def signed_byte(self):
        return self._unpack('b')

    def unsigned_word(self):
        return self._unpack('H')

    def signed_word(self):
        return self._unpack('h')

    def immediate(self, width):
        if width == 1:
            return self.unsigned_byte()
        elif width == 2:
            return self.unsigned_word()
        else:
            raise ValueError("invalid immediate width {}".format(width))

    def displacement(self, width):
        if width == 0:
            return 0
        elif width == 1:
            return self.signed_byte()
        elif width == 2:
            return self.signed_word()
        else:
            raise ValueError("invalid displacement width {}".format(width))


class Encoder:
    def __init__(self):
        self.buf = bytearray()

    def _pack(self, fmt, *items):
        offset = len(self.buf)
        self.buf += b'\x00' * struct.calcsize(fmt)
        struct.pack_into('<' + fmt, self.buf, offset, *items)

    def unsigned_byte(self, value):
        self._pack('B', value)

    def signed_byte(self, value):
        self._pack('b', value)

    def unsigned_word(self, value):
        self._pack('H', value)

    def signed_word(self, value):
        self._pack('h', value)

    def immediate(self, value, width):
        if width == 1:
            self.unsigned_byte(value)
        elif width == 2:
            self.unsigned_word(value)
        else:
            raise ValueError("invalid immediate width {}".format(width))

    def displacement(self, value, width):
        if width == 0:
            pass
        elif width == 1:
            self.signed_byte(value)
        elif width == 2:
            self.signed_word(value)
        else:
            raise ValueError("invalid displacement width {}".format(width))

