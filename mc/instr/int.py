from binaryninja.enums import BranchType
from binaryninja.lowlevelil import LowLevelILLabel

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['IntImm', 'Int3', 'Into']


class Int(Instruction):
    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        info.add_branch(BranchType.SystemCall, 4 * self.number)

    def lift(self, il, addr):
        if self.number == 3:
            il.append(il.breakpoint())
        else:
            # This *is* a trap, but if we lift it as a trap, BN assumes that execution
            # will not continue afterwards. So, to aid analysis, we add an explicit call
            # to the vector.
            # Not quite semantically correct, but good enough and useful.
            # TODO: represent this as a system call
            cs, ip = self._lift_load_cs_ip(il, il.const_pointer(2, self.number * 4))
            il.append(il.call(self._lift_phys_addr(il, cs, ip)))


class IntImm(Int):
    def name(self):
        return 'int'

    def length(self):
        return 2

    def decode(self, decoder, addr):
        Int.decode(self, decoder, addr)
        self.number = decoder.unsigned_byte()

    def encode(self, encoder, addr):
        Int.encode(self, encoder, addr)
        encoder.unsigned_byte(self.number)

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('int', fmt_dec(self.number), self.number)
        )
        return tokens


class Int3(Int):
    number = 3

    def name(self):
        return 'int3'


class Into(Int):
    number = 4

    def name(self):
        return 'into'

    def lift(self, il, addr):
        overflow_label = LowLevelILLabel()
        normal_label   = LowLevelILLabel()
        il.append(il.if_expr(il.flag('o'), overflow_label, normal_label))
        il.mark_label(overflow_label)
        Int.lift(self, il, addr)
        il.mark_label(normal_label)
