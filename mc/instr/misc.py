from binaryninja.enums import BranchType

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Hlt', 'Wait', 'Lock']


class Hlt(Instruction):
    def name(self):
        return 'hlt'

    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        info.add_branch(BranchType.UnresolvedBranch)

    def lift(self, il, addr):
        il.append(il.no_ret())


class Wait(Instruction):
    def name(self):
        return 'wait'

    def lift(self, il, addr):
        il.append(il.nop())


class Lock(Prefix):
    def name(self):
        return 'lock'

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += self.next.render(addr + 1)
        return tokens

    def lift(self, il, addr):
        il.append(il.unimplemented())
