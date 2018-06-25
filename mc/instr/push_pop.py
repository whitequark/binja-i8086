from ..helpers import *
from ..tables import *
from . import *


__all__ = ['PushReg', 'PopReg', 'PushSeg', 'PopSeg']


class PushPopReg(Instruction):
    def reg(self):
        return reg16[self.opcode & 0b111]

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('reg', self.reg())
        )
        return tokens

class PushReg(PushPopReg):
    def name(self):
        return 'push'

    def lift(self, il, addr):
        il.append(il.push(2, il.reg(2, self.reg())))

class PopReg(PushPopReg):
    def name(self):
        return 'pop'

    def lift(self, il, addr):
        il.append(il.set_reg(2, self.reg(), il.pop(2)))

class PushPopSeg(object):
    def reg(self):
        return reg_seg[(self.opcode & 0b111000) >> 3]

class PushSeg(PushPopSeg, PushReg):
    pass

class PopSeg(PushPopSeg, PopReg):
    pass
