from ..helpers import *
from ..tables import *
from . import *


__all__ = ['IncDecReg', 'IncDecRM']


class IncDec(Instruction):
    def delta(self):
        return -1 if self.name() == 'dec' else 1


class IncDecReg(IncDec):
    def name(self):
        if self.opcode & 0b1000:
            return 'dec'
        else:
            return 'inc'

    def reg(self):
        return reg16[self.opcode & 0b111]

    def render(self, addr):
        tokens = IncDec.render(self, addr)
        tokens += asm(
            ('reg', self.reg())
        )
        return tokens

    def lift(self, il, addr):
        value = il.reg(2, self.reg())
        value = il.add(2, value, il.const(2, self.delta()), '*')
        il.append(il.set_reg(2, self.reg(), value))


class IncDecRM(InstrHasModRM, InstrHasWidth, IncDec):
    def name(self):
        if self._reg_bits() & 0b001:
            return 'dec'
        else:
            return 'inc'

    def render(self, addr):
        tokens = IncDec.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        w = self.width()
        value = self._lift_reg_mem(il)
        value = il.add(w, value, il.const(w, self.delta()), '*')
        il.append(self._lift_reg_mem(il, store=value))
