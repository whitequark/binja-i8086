from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Unassigned', 'UnassignedRM']


class Unassigned(Instruction):
    def name(self):
        return '(unassigned)'


class UnassignedRM(InstrHasModRM, Instruction):
    def length(self):
        return 2

    def name(self):
        return '(unassigned)'
