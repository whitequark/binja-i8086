from binaryninja.lowlevelil import LLIL_TEMP

from ..helpers import *
from ..tables import *


__all__ = ['Instruction', 'Prefix',
           'InstrHasWidth', 'Instr16Bit',
           'InstrHasImm',
           'InstrHasSegment', 'InstrHasDisp', 'InstrHasModRegRM']


a20_gate = True


class Instruction(object):
    opcodes = {}

    def __new__(cls, decoder=None):
        if decoder is None:
            return object.__new__(cls)
        else:
            cls = cls.opcodes[decoder.peek(0)]
            if isinstance(cls, dict):
                cls = cls[(decoder.peek(1) & 0b111000) >> 3]
            return object.__new__(cls)

    def name(self):
        return 'unimplemented'

    def length(self):
        return 1

    def total_length(self):
        return self.length()

    def decode(self, decoder, addr):
        self.opcode = decoder.unsigned_byte()

    def encode(self, encoder, addr):
        encoder = encoder.unsigned_byte(self.opcode)

    def analyze(self, info, addr):
        info.length += self.length()

    def render(self, addr):
        return asm(
            ('instr', self.name()),
            ('opsep', ' ' * (8 - len(self.name())))
        )

    def lift(self, il, addr):
        il.append(il.unimplemented())

    def _lift_phys_addr(self, il, seg, disp):
        if seg in il.arch.regs:
            seg = il.reg(2, seg)
        if disp in il.arch.regs:
            disp = il.reg(2, disp)
        base = il.shift_left(3, seg, il.const(1, 4))
        phys = il.add(3, base, disp)
        if a20_gate:
            phys = il.and_expr(3, il.const(3, 0xfffff), phys)
        return phys

    def _lift_load_cs_ip(self, il, addr):
        cs_ip  = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(4, cs_ip, il.load(4, addr)))
        cs     = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(2, cs, il.logical_shift_right(2, il.reg(4, cs_ip), il.const(1, 16))))
        ip     = LLIL_TEMP(il.temp_reg_count)
        il.append(il.set_reg(2, ip, il.low_part(2, il.reg(4, cs_ip))))
        return il.reg(2, cs), il.reg(2, ip)


class Prefix(Instruction):
    def decode(self, decoder, addr):
        Instruction.decode(self, decoder, addr)
        try:
            self.next = Instruction(decoder)
        except KeyError:
            self.next = Instruction()
        self.next.decode(decoder, addr)

    def encode(self, encoder, addr):
        Instruction.encode(self, encoder, addr)
        self.next.encode(encoder, addr + 1)

    def total_length(self):
        return self.length() + self.next.length()

    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        self.next.analyze(info, addr + 1)

    def render(self, addr):
        return self.next.render(addr + 1)

    def lift(self, il, addr):
        self.next.lift(il, addr + 1)


class InstrHasWidth(object):
    def width(self):
        return 1 + (self.opcode & 0b1)

    def _regW(self):
        if self.width() == 2:
            return reg16
        else:
            return reg8


class Instr16Bit(object):
    def width(self):
        return 2

    def _regW(self):
        return reg16


class InstrHasImm(object):
    def length(self):
        return super(InstrHasImm, self).length() + self.width()

    def decode(self, decoder, addr):
        super(InstrHasImm, self).decode(decoder, addr)
        self.imm = decoder.immediate(self.width())

    def encode(self, encoder, addr):
        super(InstrHasImm, self).encode(encoder, addr)
        encoder.immediate(self.imm, self.width())


class InstrHasSegment(object):
    segment_override = None

    def segment(self):
        if self.segment_override:
            return self.segment_override
        else:
            return self._default_segment()

    def _default_segment(self):
        return 'ds'

class InstrHasDisp(InstrHasSegment):
    def length(self):
        return Instruction.length(self) + 2

    def decode(self, decoder, addr):
        Instruction.decode(self, decoder, addr)
        self.disp = decoder.displacement(2)

    def encode(self, encoder, addr):
        Instruction.encode(self, encoder, addr)
        encoder.displacement(self.disp, 2)

    def _render_mem(self):
        tokens = asm(
            ('beginMem', '[')
        )
        if self.segment() != self._default_segment():
            tokens += asm(
                ('reg', self.segment()),
                ('opsep', ':')
            )
        tokens += asm(
            ('addr', fmt_disp(self.disp), self.disp),
            ('endMem', ']'),
        )
        return tokens

    def _lift_mem(self, il, store=None):
        w = self.width()
        phys = self._lift_phys_addr(il, self.segment(), il.const(2, self.disp))
        if store is None:
            return il.load(w, phys)
        else:
            return il.store(w, phys, store)


class InstrHasModRegRM(InstrHasSegment):
    def length(self):
        return super(InstrHasModRegRM, self).length() + 1 + self._disp_length()

    def decode(self, decoder, addr):
        super(InstrHasModRegRM, self).decode(decoder, addr)
        self._mod_reg_rm = decoder.unsigned_byte()
        self.disp = decoder.displacement(self._disp_length())

    def encode(self, encoder, addr):
        super(InstrHasModRegRM, self).encode(encoder, addr)
        encoder.unsigned_byte(self._mod_reg_rm)
        encoder.displacement(self.disp, self._disp_length())

    def _default_segment(self):
        if self._mod_bits() == 0b00 and self._reg_mem_bits() == 0b110:
            return 'ds'
        elif self._mod_bits() != 0b11 and 'bp' in self._mem_regs():
            return 'ss'
        else:
            return 'ds'

    def _mod_bits(self):
        return self._mod_reg_rm >> 6

    def _reg_bits(self):
        return (self._mod_reg_rm >> 3) & 0b111

    def _reg_mem_bits(self):
        return self._mod_reg_rm & 0b111

    def _reg(self):
        return self._regW()[self._reg_bits()]

    def _mem_regs(self):
        return regs_rm[self._reg_mem_bits()]

    def _reg2(self):
        return self._regW()[self._reg_mem_bits()]

    def _disp_length(self):
        if self._mod_bits() == 0b00 and self._reg_mem_bits() == 0b110:
            return 2
        elif self._mod_bits() == 0b10:
            return 2
        elif self._mod_bits() == 0b01:
            return 1
        return 0

    def _render_reg_mem(self, fixed_width=False):
        if self._mod_bits() == 0b11:
            return asm(
                ('reg', self._reg2())
            )
        elif self._mod_bits() == 0b00 and self._reg_mem_bits() == 0b110:
            disp = self.disp & 0xffff
            tokens = [
                ('int', fmt_disp(disp), disp)
            ]
        else:
            tokens = map(lambda reg: ('reg', reg), self._mem_regs())
            if len(tokens) == 2:
                tokens.insert(1, ('text', '+'))
            if self._mod_bits() != 0b00:
                tokens += [
                    ('int', fmt_hex_sign(self.disp), self.disp)
                ]
        if self.segment() != self._default_segment():
            tokens = [
                ('reg', self.segment()),
                ('opsep', ':')
            ] + tokens
        tokens = [
            ('beginMem', '[')
        ] + tokens + [
            ('endMem', ']')
        ]
        if not fixed_width:
            tokens = [
                ('text', op_width[self.opcode & 0b1]),
                ('opsep', ' '),
            ] + tokens
        return asm(*tokens)

    def _lift_reg_mem(self, il, store=None, only_calc_addr=False):
        if self._mod_bits() == 0b11:
            if only_calc_addr:
                # MOD=11 is not expressly prohibited for LEA in the manual.
                return il.reg(2, self._reg2())
            if store is None:
                return il.reg(self.width(), self._reg2())
            else:
                return il.set_reg(self.width(), self._reg2(), store)
        elif self._mod_bits() == 0b00 and self._reg_mem_bits() == 0b110:
            offset = il.const(2, self.disp & 0xffff)
        else:
            offsets = map(lambda reg: il.reg(2, reg), self._mem_regs())
            if self._mod_bits() != 0b00:
                offsets.append(il.const(2, self.disp))
            offset = reduce(lambda expr, reg: il.add(2, expr, reg), offsets)
        if only_calc_addr:
            return offset
        phys = self._lift_phys_addr(il, self.segment(), offset)
        if store is None:
            return il.load(self.width(), phys)
        else:
            return il.store(self.width(), phys, store)
