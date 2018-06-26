from binaryninja.lowlevelil import LLIL_TEMP

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Nop', 'Xchg']


class Nop(Instruction):
    def name(self):
        return 'nop'

    def lift(self, il, addr):
        il.append(il.nop())


class Xchg(Instruction):
    def name(self):
        return 'xchg'

    def reg1(self):
        return 'ax'

    def reg2(self):
        return reg16[self.opcode & 0b111]

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('reg', self.reg1()),
            ('opsep', ', '),
            ('reg', self.reg2()),
        )
        return tokens

    def lift(self, il, addr):
        temp = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(2, temp, il.reg(2, self.reg1())))
        il.append(il.set_reg(2, self.reg1(), il.reg(2, self.reg2())))
        il.append(il.set_reg(2, self.reg2(), il.reg(2, temp)))
