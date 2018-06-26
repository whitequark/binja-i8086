from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Segment']


class Segment(Prefix):
    def reg_seg(self):
        return reg_seg[(self.opcode & 0b11000) >> 3]

    def decode(self, decoder, addr):
        Prefix.decode(self, decoder, addr)
        if hasattr(self.next, 'segment_override'):
            self.next.segment_override = self.reg_seg()

    def render(self, addr):
        if hasattr(self.next, 'segment_override'):
            tokens = []
        else:
            tokens = asm(
                ('reg', self.reg_seg()),
                ('opsep', ' ')
            )
        tokens += self.next.render(addr + 1)
        return tokens
