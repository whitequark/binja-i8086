from ..helpers import *
from ..tables import *
from . import *


__all__ = ['MovRegImm', 'MovMemImm', 'MovRMReg', 'MovRegRM',
           'MovAccMem', 'MovMemAcc', 'MovRMSeg', 'MovSegRM']


class Mov(Instruction):
    default_segment = 'ds'

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


class MovMemImm(InstrHasImm, InstrHasModRM, InstrHasWidth, Mov):
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


class MovRMReg(InstrHasModRM, InstrHasWidth, Mov):
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


class MovRegRM(InstrHasModRM, InstrHasWidth, Mov):
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


class MovRMSeg(InstrHasModRM, Instr16Bit, Mov):
    def src_reg(self):
        return reg_seg[self._reg_bits()]

    def render(self, addr):
        if self._reg_bits() & 0b100:
            return asm(('instr', 'invalid'))

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


class MovSegRM(InstrHasModRM, Instr16Bit, Mov):
    def dst_reg(self):
        return reg_seg[self._reg_bits()]

    def render(self, addr):
        if self._reg_bits() & 0b100:
            return asm(('instr', 'invalid'))

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