from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Unassigned', 'UnassignedRM']


class Unassigned(Instruction):
    def name(self):
        return '(unassigned)'

    def lift(self, il, addr):
        il.append(il.undefined())


class UnassignedRM(InstrHasModRegRM, Unassigned):
    def length(self):
        return 2
