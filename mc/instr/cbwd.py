from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Cbw', 'Cwd']


class Cbw(Instruction):
    def name(self):
        return 'cbw'

    def lift(self, il, addr):
        il.append(il.set_reg(2, 'ax', il.sign_extend(2, il.reg(1, 'al'))))


class Cwd(Instruction):
    def name(self):
        return 'cwd'

    def lift(self, il, addr):
        il.append(il.set_reg_split(4, 'dx', 'ax', il.sign_extend(4, il.reg(2, 'ax'))))
