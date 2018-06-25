from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Clc', 'Stc', 'Cmc', 'Cli', 'Sti', 'Cld', 'Std']


class Clc(Instruction):
    def name(self):
        return 'clc'

    def lift(self, il, addr):
        il.append(il.set_flag('c', il.const(1, 0)))


class Stc(Instruction):
    def name(self):
        return 'stc'

    def lift(self, il, addr):
        il.append(il.set_flag('c', il.const(1, 1)))


class Cmc(Instruction):
    def name(self):
        return 'cmc'

    def lift(self, il, addr):
        il.append(il.set_flag('c', il.neg_expr(1, il.flag('c'))))


class Cli(Instruction):
    def name(self):
        return 'cli'

    def lift(self, il, addr):
        il.append(il.set_flag('i', il.const(1, 0)))


class Sti(Instruction):
    def name(self):
        return 'sti'

    def lift(self, il, addr):
        il.append(il.set_flag('i', il.const(1, 1)))


class Cld(Instruction):
    def name(self):
        return 'cld'

    def lift(self, il, addr):
        il.append(il.set_flag('d', il.const(1, 0)))


class Std(Instruction):
    def name(self):
        return 'std'

    def lift(self, il, addr):
        il.append(il.set_flag('d', il.const(1, 1)))
