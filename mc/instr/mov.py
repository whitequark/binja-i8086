from ..helpers import *
from ..tables import *
from . import *


__all__ = ['MovRegImm', 'MovMemImm',
           'MovRMReg',  'MovRegRM',
           'MovAccMem', 'MovMemAcc',
           'MovRMSeg',  'MovSegRM',
           'LSegRegRM',
           'Xlat',
           'SahF', 'LahF']


class Mov(Instruction):
    def name(self):
        return 'mov'


class MovRegImm(InstrHasImm, InstrHasWidth, Mov):
    def width(self):
        return 1 + ((self.opcode & 0b1000) >> 3)

    def dst_reg(self):
        return self._regW()[self.opcode & 0b0111]

    def render(self, addr):
        tokens = Mov.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
            ('int', fmt_imm(self.imm), self.imm)
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(il.set_reg(w, self.dst_reg(), il.const(w, self.imm)))


class MovMemImm(InstrHasImm, InstrHasModRegRM, InstrHasWidth, Mov):
    def render(self, addr):
        if self._reg_bits() != 0b000:
            return Mov.render(self) + asm(
                ('text', 'illegal')
            )

        tokens = Mov.render(self, addr)
        tokens += self._render_reg_mem()
        tokens += asm(
            ('opsep', ', '),
            ('int', fmt_imm(self.imm), self.imm)
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(self._lift_reg_mem(il, store=il.const(w, self.imm)))


class MovRMReg(InstrHasModRegRM, InstrHasWidth, Mov):
    def src_reg(self):
        return self._reg()

    def render(self, addr):
        tokens = Mov.render(self, addr)
        tokens += self._render_reg_mem()
        tokens += asm(
            ('opsep', ', '),
            ('reg', self.src_reg()),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(self._lift_reg_mem(il, store=il.reg(w, self.src_reg())))


class MovRegRM(InstrHasModRegRM, InstrHasWidth, Mov):
    def dst_reg(self):
        return self._reg()

    def render(self, addr):
        tokens = Mov.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
        )
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(il.set_reg(w, self.dst_reg(), self._lift_reg_mem(il)))


class MovMem(InstrHasDisp, InstrHasWidth, Mov):
    def length(self):
        return Instruction.length(self) + 2

    def decode(self, decoder, addr):
        Instruction.decode(self, decoder, addr)
        self.disp = decoder.displacement(2)

    def encode(self, encoder, addr):
        Instruction.encode(self, encoder, addr)
        encoder.displacement(self.disp, 2)


class MovAccMem(MovMem):
    def dst_reg(self):
        return 'ax' if self.width() == 2 else 'al'

    def render(self, addr):
        tokens = MovMem.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', ')
        )
        tokens += self._render_mem()
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(il.set_reg(w, self.dst_reg(), self._lift_mem(il)))


class MovMemAcc(MovMem):
    def src_reg(self):
        return 'ax' if self.width() == 2 else 'al'

    def render(self, addr):
        tokens = MovMem.render(self, addr)
        tokens += self._render_mem()
        tokens += asm(
            ('opsep', ', '),
            ('reg', self.src_reg()),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        il.append(self._lift_mem(il, store=il.reg(w, self.src_reg())))


class MovRMSeg(InstrHasModRegRM, Instr16Bit, Mov):
    def src_reg(self):
        return reg_seg[self._reg_bits()]

    def render(self, addr):
        if self._reg_bits() & 0b100:
            return asm(('instr', '(unassigned)'))

        tokens = Mov.render(self, addr)
        tokens += self._render_reg_mem(fixed_width=True)
        tokens += asm(
            ('opsep', ', '),
            ('reg', self.src_reg()),
        )
        return tokens

    def lift(self, il, addr):
        if self._reg_bits() & 0b100:
            il.append(il.undefined())
            return

        il.append(self._lift_reg_mem(il, store=il.reg(2, self.src_reg())))


class MovSegRM(InstrHasModRegRM, Instr16Bit, Mov):
    def dst_reg(self):
        return reg_seg[self._reg_bits()]

    def render(self, addr):
        if self._reg_bits() & 0b100:
            return asm(('instr', '(unassigned)'))

        tokens = Mov.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
        )
        tokens += self._render_reg_mem(fixed_width=True)
        return tokens

    def lift(self, il, addr):
        if self._reg_bits() & 0b100:
            il.append(il.undefined())
            return

        il.append(il.set_reg(2, self.dst_reg(), self._lift_reg_mem(il)))


class LSegRegRM(InstrHasModRegRM, Instr16Bit, Instruction):
    def name(self):
        return 'l' + self.seg_reg()

    def seg_reg(self):
        if self.opcode & 0b1:
            return 'ds'
        else:
            return 'es'

    def dst_reg(self):
        return self._reg()

    def render(self, addr):
        if self._mod_bits() == 0b11:
            return asm(('instr', '(unassigned)'))

        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
        )
        tokens += self._render_reg_mem(fixed_width=True)
        return tokens

    def lift(self, il, addr):
        if self._mod_bits() == 0b11:
            il.append(il.undefined())
            return

        seg, off = self._lift_load_far(il, self._lift_reg_mem(il))
        il.append(il.set_reg(2, self.seg_reg(), seg))
        il.append(il.set_reg(2, self.dst_reg(), off))


class Xlat(InstrHasSegment, Instruction):
    def name(self):
        return 'xlat'

    def lift(self, il, addr):
        off  = il.add(2, il.reg(2, 'bx'), il.reg(1, 'al'))
        phys = self._lift_phys_addr(il, self.segment(), off)
        il.append(il.set_reg(1, 'al', il.load(1, phys)))


class LahF(Instruction):
    def name(self):
        return 'lahf'

    def lift(self, il, addr):
        flags = il.const(1, 0b10)
        for flag, flag_bit in flags_bits:
            if flag_bit > 7:
                break
            bit = il.flag_bit(1, flag, flag_bit)
            flags = il.or_expr(1, bit, flags)
        il.append(il.set_reg(1, 'ah', flags))


class SahF(Instruction):
    def name(self):
        return 'sahf'

    def lift(self, il, addr):
        for flag, flag_bit in flags_bits:
            if flag_bit > 7:
                break
            bit = il.test_bit(1, il.reg(1, 'ah'), il.const(1, flag_bit))
            il.append(il.set_flag(flag, bit))
