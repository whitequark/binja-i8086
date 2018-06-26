from binaryninja.enums import BranchType
from binaryninja.lowlevelil import LowLevelILLabel

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['JmpFarImm', 'JmpFarMem',
           'JmpNearImm', 'JmpNearRM',
           'JmpShort', 'JmpCond',
           'Loop', 'Loope', 'Loopne', 'Jcxz']


class Jmp(Instruction):
    def name(self):
        return 'jmp'


class JmpFarImm(Jmp):
    def length(self):
        return 5

    def decode(self, decoder, addr):
        Jmp.decode(self, decoder, addr)
        self.ip = decoder.unsigned_word()
        self.cs = decoder.unsigned_word()

    def encode(self, encoder, addr):
        Jmp.encode(self, encoder, addr)
        encoder.unsigned_word(self.ip)
        encoder.unsigned_word(self.cs)

    def target(self):
        return (self.cs << 4) + self.ip

    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.UnconditionalBranch, self.target())

    def render(self, addr):
        tokens = Jmp.render(self, addr)
        tokens += asm(
            ('addr', fmt_code_abs(self.cs), self.cs << 4),
            ('opsep', ':'),
            ('addr', fmt_code_abs(self.ip), self.target()),
        )
        return tokens

    def lift(self, il, addr):
        il.append(il.set_reg(2, 'cs', il.const(2, self.cs)))
        il.append(il.jump(il.const(3, self.target())))


class JmpFarMem(InstrHasModRM, Instr16Bit, Jmp):
    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.IndirectBranch)

    def render(self, addr):
        if self._mod_bits() == 0b11:
            return asm(('instr', '(unassigned)'))

        tokens = Jmp.render(self, addr)
        tokens += asm(
            ('text', 'far'),
            ('opsep', ' '),
        )
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        if self._mod_bits() == 0b11:
            il.append(il.undefined())
            return

        il.append(il.unimplemented())


class JmpNearImm(Jmp):
    def length(self):
        return 3

    def decode(self, decoder, addr):
        Jmp.decode(self, decoder, addr)
        self.ip = addr + self.length() + decoder.signed_word()

    def encode(self, encoder, addr):
        Jmp.encode(self, encoder, addr)
        encoder.signed_word(self.ip - addr - self.length())

    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.UnconditionalBranch, self.ip)

    def render(self, addr):
        tokens = Jmp.render(self, addr)
        tokens += asm(
            ('codeRelAddr', fmt_code_rel(self.ip - addr), self.ip),
        )
        return tokens

    def lift(self, il, addr):
        label = il.get_label_for_address(il.arch, self.ip)
        if label is None:
            il.append(il.jump(il.const(3, self.ip)))
        else:
            il.append(il.goto(label))


class JmpNearRM(InstrHasModRM, Instr16Bit, Jmp):
    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.IndirectBranch)

    def render(self, addr):
        tokens = Jmp.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        il.append(il.jump(self._lift_addr(il, 'cs', self._lift_reg_mem(il))))


class JmpShort(Jmp):
    def length(self):
        return 2

    def decode(self, decoder, addr):
        Jmp.decode(self, decoder, addr)
        self.ip = addr + self.length() + decoder.signed_byte()

    def encode(self, encoder, addr):
        Jmp.encode(self, encoder, addr)
        encoder.signed_byte(self.ip - addr - self.length())

    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.UnconditionalBranch, self.ip)

    def render(self, addr):
        tokens = Jmp.render(self, addr)
        tokens += asm(
            ('codeRelAddr', fmt_code_rel(self.ip - addr), self.ip),
        )
        return tokens

    def lift(self, il, addr):
        label = il.get_label_for_address(il.arch, self.ip)
        if label is None:
            il.append(il.jump(il.const(3, self.ip)))
        else:
            il.append(il.goto(label))


class JmpCond(JmpShort):
    def name(self):
        return instr_jump[self.opcode & 0b1111]

    def to_always(self):
        branch = JmpShort()
        branch.opcode = 0xeb
        branch.ip     = self.ip
        return branch

    def to_inverted(self):
        branch = JmpCond()
        branch.opcode = self.opcode ^ 0b0001
        branch.ip     = self.ip
        return branch

    def analyze(self, info, addr):
        Jmp.analyze(self, info, addr)
        info.add_branch(BranchType.TrueBranch, self.ip)
        info.add_branch(BranchType.FalseBranch, addr + self.length())

    def lift(self, il, addr):
        untaken_label = il.get_label_for_address(il.arch, addr + self.length())
        taken_label   = il.get_label_for_address(il.arch, self.ip)
        if taken_label is None:
            mark_taken = True
            taken_label = LowLevelILLabel()
        else:
            mark_taken = False

        name = self.name()
        if name == 'jpe':
            il.append(il.if_expr(il.flag('p'), taken_label, untaken_label))
        elif name == 'jpo':
            il.append(il.if_expr(il.flag('p'), untaken_label, taken_label))
        else:
            cond = jump_cond[name]
            il.append(il.if_expr(il.flag_condition(cond), taken_label, untaken_label))

        if mark_taken:
            il.mark_label(taken_label)
            il.append(il.jump(il.const(3, self.ip)))


class Loop(JmpCond):
    def name(self):
        return instr_loop[self.opcode & 0b11]

    def _lift_loop_cond(self, il):
        il.append(il.set_reg(2, 'cx', il.sub(2, il.reg(2, 'cx'), il.const(2, 1))))
        cond = il.compare_not_equal(2, il.reg(2, 'cx'), il.const(2, 0))
        if hasattr(self, '_lift_loop_pred'):
            cond = il.and_expr(1, cond, self._lift_loop_pred(il))
        return cond

    def lift(self, il, addr):
        untaken_label = il.get_label_for_address(il.arch, addr + self.length())
        taken_label   = il.get_label_for_address(il.arch, self.ip)
        if taken_label is None:
            mark_taken = True
            taken_label = LowLevelILLabel()
        else:
            mark_taken = False

        il.append(il.if_expr(self._lift_loop_cond(il), taken_label, untaken_label))
        if mark_taken:
            il.mark_label(taken_label)
            il.append(il.jump(il.const(3, self.ip)))


class Loope(Loop):
    def _lift_loop_pred(self, il):
        return il.flag('e')


class Loopne(Loop):
    def _lift_loop_pred(self, il):
        return il.not_expr(il.flag('e'))


class Jcxz(Loop):
    def _lift_loop_cond(self, il):
        return il.compare_equal(2, il.reg(2, 'cx'), il.const(2, 0))
