from ..helpers import *
from ..tables import *
from . import *


__all__ = ['PushReg', 'PopReg',
           'PushSeg', 'PopSeg',
           'PushRM',  'PopRM']


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


class PushRM(InstrHasModRM, Instr16Bit, Instruction):
    default_segment = 'ds'

    def name(self):
        return 'push'

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        il.append(il.push(2, self._lift_reg_mem(il)))


class PopRM(InstrHasModRM, Instr16Bit, Instruction):
    default_segment = 'ds'

    def name(self):
        return 'pop'

    def render(self, addr):
        if self._reg_bits() != 0b000:
            return asm(('instr', '(unassigned)'))

        tokens = Instruction.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        if self._reg_bits() != 0b000:
            il.append(il.undefined())
            return

        il.append(il.push(2, self._lift_reg_mem(il)))
