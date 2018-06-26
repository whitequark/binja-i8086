from binaryninja.enums import BranchType
from binaryninja.lowlevelil import LLIL_TEMP

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['CallFarImm', 'CallFarMem', 'CallNearImm', 'CallNearRM']


class Call(Instruction):
    def name(self):
        return 'call'


class CallFarImm(Call):
    def length(self):
        return 5

    def decode(self, decoder, addr):
        Call.decode(self, decoder, addr)
        self.ip = decoder.unsigned_word()
        self.cs = decoder.unsigned_word()

    def encode(self, encoder, addr):
        Call.encode(self, encoder, addr)
        encoder.unsigned_word(self.ip)
        encoder.unsigned_word(self.cs)

    def target(self):
        return (self.cs << 4) + self.ip

    def analyze(self, info, addr):
        Call.analyze(self, info, addr)
        info.add_branch(BranchType.CallDestination, self.target())

    def render(self, addr):
        tokens = Call.render(self, addr)
        tokens += asm(
            ('addr', fmt_code_abs(self.cs), self.cs << 4),
            ('opsep', ':'),
            ('addr', fmt_code_abs(self.ip), self.target()),
        )
        return tokens

    def lift(self, il, addr):
        # CS is (if the calling convention matches, anyway) popped by the callee, but we
        # explicitly restore it at the call site because the callee may not be statically
        # known, and that it restores CS is a safe assumption.
        # Not quite semantically correct, but good enough and useful.
        temp = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(2, temp, il.reg(2, 'cs')))
        il.append(il.push(2, il.reg(2, 'cs')))
        il.append(il.set_reg(2, 'cs', il.const(2, self.cs)))
        il.append(il.call_stack_adjust(il.const(3, self.target()), 2))
        il.append(il.set_reg(2, 'cs', il.reg(2, temp)))


class CallFarMem(InstrHasModRegRM, Instr16Bit, Call):
    def analyze(self, info, addr):
        Call.analyze(self, info, addr)
        # FIXME: what should we do for indirect calls?
        # info.add_branch(BranchType.CallDestination)

    def render(self, addr):
        if self._mod_bits() == 0b11:
            return asm(('instr', '(unassigned)'))

        tokens = Call.render(self, addr)
        tokens += asm(
            ('text', 'far'),
            ('opsep', ' '),
        )
        tokens += self._render_reg_mem(fixed_width=True)
        return tokens

    def lift(self, il, addr):
        if self._mod_bits() == 0b11:
            il.append(il.undefined())
            return

        cs, ip = self._lift_load_cs_ip(il, self._lift_reg_mem(il))
        il.append(il.set_reg(2, 'cs', cs))
        old_cs = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(2, old_cs, il.reg(2, 'cs')))
        il.append(il.push(2, il.reg(2, 'cs')))
        il.append(il.call_stack_adjust(self._lift_phys_addr(il, cs, ip), 2))
        il.append(il.set_reg(2, 'cs', il.reg(2, old_cs)))


class CallNearImm(Call):
    def length(self):
        return 3

    def decode(self, decoder, addr):
        Call.decode(self, decoder, addr)
        self.ip = addr + self.length() + decoder.signed_word()

    def encode(self, encoder, addr):
        Call.encode(self, encoder, addr)
        encoder.signed_word(self.ip - addr - self.length())

    def analyze(self, info, addr):
        Call.analyze(self, info, addr)
        info.add_branch(BranchType.CallDestination, self.ip)

    def render(self, addr):
        ip_rel = self.ip - addr
        tokens = Call.render(self, addr)
        tokens += asm(
            ('codeRelAddr', fmt_code_rel(ip_rel), ip_rel),
        )
        return tokens

    def lift(self, il, addr):
        il.append(il.call(il.const(3, self.ip)))


class CallNearRM(InstrHasModRegRM, Instr16Bit, Call):
    def _default_segment(self):
        return 'cs'

    def analyze(self, info, addr):
        Call.analyze(self, info, addr)
        # FIXME: what should we do for indirect calls?
        # info.add_branch(BranchType.CallDestination)

    def render(self, addr):
        tokens = Call.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        il.append(il.call(self._lift_phys_addr(il, self.segment(), self._lift_reg_mem(il))))
