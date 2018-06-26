from binaryninja import log

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
    except (KeyError, coding.BufferTooShort):
        log.log_warn('At address {:05x}:'.format(addr))
        log.log_warn('Error decoding {}'.format(data.encode('hex')))
        pass

def encode(instr, addr):
    encoder = Encoder()
    instr.encode(encoder, addr)
    return bytes(encoder.buf)
