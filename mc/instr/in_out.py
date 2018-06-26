from binaryninja.lowlevelil import ILRegister, LLIL_TEMP

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['InImm', 'OutImm', 'InReg', 'OutReg']


class In(Instruction):
    def name(self):
        return 'in'

    def dst_reg(self):
        return 'ax' if self.width() == 2 else 'al'

class Out(Instruction):
    def name(self):
        return 'out'

    def src_reg(self):
        return 'ax' if self.width() == 2 else 'al'

class InOutImm:
    def length(self):
        return Instruction.length(self) + self.width()

    def decode(self, decoder, addr):
        Instruction.decode(self, decoder, addr)
        self.imm = decoder.immediate(self.width())

    def encode(self, encoder, addr):
        Instruction.encode(self, encoder, addr)
        encoder.immediate(self.imm, self.width())


class InImm(InstrHasWidth, InOutImm, In):
    def render(self, addr):
        tokens = In.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
            ('int', fmt_hexW(self.imm, self.width()), self.imm)
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        name = 'inw' if w == 2 else 'inb'
        # If assigning directly to ax, either the entire register needs to be assigned,
        # or the SSA translation misidentifiers registers. Not sure why, BN bug?
        temp = LLIL_TEMP(il.temp_reg_count)
        il.append(il.intrinsic([ILRegister(il.arch, temp)], name, [il.const(2, self.imm)]))
        il.append(il.set_reg(w, self.dst_reg(), il.reg(w, temp)))


class InReg(InstrHasWidth, In):
    def render(self, addr):
        tokens = In.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
            ('reg', 'dx')
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        name = 'inw' if w == 2 else 'inb'
        # See above.
        temp = LLIL_TEMP(il.temp_reg_count)
        il.append(il.intrinsic([ILRegister(il.arch, temp)], name, [il.reg(2, 'dx')]))
        il.append(il.set_reg(w, self.dst_reg(), il.reg(w, temp)))


class OutImm(InstrHasWidth, InOutImm, Out):
    def render(self, addr):
        tokens = Out.render(self, addr)
        tokens += asm(
            ('int', fmt_hexW(self.imm, self.width()), self.imm),
            ('opsep', ', '),
            ('reg', self.src_reg())
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        name = 'outw' if w == 2 else 'outb'
        il.append(il.intrinsic([], name, [il.const(2, self.imm), il.reg(w, self.src_reg())]))


class OutReg(InstrHasWidth, Out):
    def render(self, addr):
        tokens = Out.render(self, addr)
        tokens += asm(
            ('reg', 'dx'),
            ('opsep', ', '),
            ('reg', self.src_reg())
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        name = 'outw' if w == 2 else 'outb'
        il.append(il.intrinsic([], name, [il.reg(2, 'dx'), il.reg(w, self.src_reg())]))
