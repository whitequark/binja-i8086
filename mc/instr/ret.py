from binaryninja.enums import BranchType

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['RetNear', 'RetNearImm']


class RetNear(Instruction):
    def name(self):
        return 'ret'

    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        info.add_branch(BranchType.FunctionReturn)

    def lift(self, il, addr):
        il.append(il.ret(il.pop(2)))


class RetNearImm(InstrHasImm, RetNear):
    def width(self):
        return 2

    def render(self, addr):
        tokens = RetNear.render(addr)
        tokens += [
            ('int', fmt_hex2(self.imm), self.imm),
        ]
        return tokens

    def lift(self, il, addr):
        il.append(il.set_reg(2, 'sp', il.add(2, il.reg(2, 'sp'), il.const(2, self.imm))))
        il.append(il.ret(il.pop(2)))
