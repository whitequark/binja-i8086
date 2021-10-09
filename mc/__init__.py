from binaryninja.log import log_warn

from .coding import *
from .instr import Instruction
from .opcodes import *


__all__ = ['decode', 'encode']


def decode(data, addr):
    decoder = Decoder(data)
    try:
        instr = Instruction(decoder)
        instr.decode(decoder, addr)
        return instr
    except KeyError:
        log_warn('At address {:05x}: unknown encoding {}'
                 .format(addr, data.hex()))
    except coding.BufferTooShort:
        pass


def encode(instr, addr):
    encoder = Encoder()
    instr.encode(encoder, addr)
    return bytes(encoder.buf)
