from ..helpers import *
from ..tables import *
from . import *


__all__ = ['TestAccImm', 'TestRegMemImm']


class Test(Instruction):
    def name(self):
        return 'test'


class TestAccImm(InstrHasImm, InstrHasWidth, Test):
    def reg(self):
        return 'ax' if self.width() == 2 else 'al'

    def render(self, addr):
        tokens = Test.render(self, addr)
        tokens += asm(
            ('reg', self.reg()),
            ('opsep', ', '),
            ('int', fmt_imm(self.imm), self.imm),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(il.and_expr(w, il.reg(w, self.reg()), il.const(w, self.imm), '*'))


class TestRegMemImm(InstrHasImm, InstrHasModRegRM, InstrHasWidth, Test):
    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += self._render_reg_mem()
        tokens += asm(
            ('opsep', ', '),
            ('int', fmt_dec(self.imm), self.imm),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(il.add(w, self._lift_reg_mem(il), il.const(w, self.imm), '*'))
