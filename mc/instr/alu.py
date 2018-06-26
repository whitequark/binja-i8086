from ..helpers import *
from ..tables import *
from . import *


__all__ = ['AluLogicRegRM',  'AluLogicRMReg',
           'AluLogicAccImm', 'AluLogicRMImm',
           'AluShiftRM',
           'AluArithRegMem']


class AluLogic(InstrHasWidth, Instruction):
    def name(self):
        return instr_alu_logic[(self.opcode & 0b111000) >> 3]

    def _op(self, il, lhs, rhs):
        if self.name() == 'add':
            result = il.add(self.width(), lhs, rhs, '*')
        elif self.name() == 'or':
            result = il.or_expr(self.width(), lhs, rhs, '*')
        elif self.name() == 'adc':
            result = il.add_carry(self.width(), lhs, rhs, il.flag('c'), '*')
        elif self.name() == 'sbb':
            result = il.sub_borrow(self.width(), lhs, rhs, il.flag('c'), '*')
        elif self.name() == 'and':
            result = il.and_expr(self.width(), lhs, rhs, '*')
        elif self.name() == 'sub':
            result = il.sub(self.width(), lhs, rhs, '*')
        elif self.name() == 'xor':
            result = il.xor_expr(self.width(), lhs, rhs, '*')
        elif self.name() == 'cmp':
            il.append(il.sub(self.width(), lhs, rhs, '*'))
            return
        return result


class AluLogicRMReg(InstrHasModRegRM, AluLogic):
    def src_reg(self):
        return self._reg()

    def render(self, addr):
        tokens = AluLogic.render(self, addr)
        tokens += self._render_reg_mem()
        tokens += asm(
            ('opsep', ', '),
            ('reg', self.src_reg()),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        result = self._op(il, self._lift_reg_mem(il), il.reg(w, self.src_reg()))
        if result:
            il.append(self._lift_reg_mem(il, store=result))


class AluLogicRegRM(InstrHasModRegRM, AluLogic):
    def dst_reg(self):
        return self._reg()

    def render(self, addr):
        tokens = AluLogic.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
        )
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        w = self.width()
        result = self._op(il, il.reg(w, self.dst_reg()), self._lift_reg_mem(il))
        if result:
            il.append(il.set_reg(w, self.dst_reg(), result))


class AluLogicAccImm(InstrHasImm, AluLogic):
    def dst_reg(self):
        return 'ax' if self.width() == 2 else 'al'

    def render(self, addr):
        tokens = AluLogic.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', '),
            ('int', fmt_imm(self.imm), self.imm),
        )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        result = self._op(il, il.reg(w, self.dst_reg()), il.const(w, self.imm))
        if result:
            il.append(il.set_reg(w, self.dst_reg(), result))


class AluLogicRMImm(InstrHasModRegRM, AluLogic):
    def name(self):
        return instr_alu_logic[self._reg_bits()]

    def _sign_extend(self):
        return (self.opcode & 0b10) >> 1

    def _imm_width(self):
        if self.width() == 2 and not self._sign_extend():
            return 2
        else:
            return 1

    def length(self):
        return InstrHasModRegRM.length(self) + self._imm_width()

    def decode(self, decoder, addr):
        InstrHasModRegRM.decode(self, decoder, addr)
        self.imm = decoder.immediate(self._imm_width())

    def encode(self, encoder, addr):
        InstrHasModRegRM.encode(self, encoder, addr)
        encoder.immediate(self.imm, self._imm_width())

    def render(self, addr):
        tokens = AluLogic.render(self, addr)
        tokens += self._render_reg_mem()
        if self._sign_extend():
            tokens += asm(
                ('opsep', ', '),
                ('text', op_width[self.opcode & 0b1]),
                ('opsep', ' '),
                ('int', fmt_imm_sign(self.imm), self.imm),
            )
        else:
            tokens += asm(
                ('opsep', ', '),
                ('int', fmt_imm(self.imm), self.imm),
            )
        return tokens

    def lift(self, il, addr):
        w = self.width()
        lhs = self._lift_reg_mem(il)
        rhs = il.const(self._imm_width(), self.imm)
        if self._sign_extend():
            rhs = il.sign_extend(w, rhs)
        result = self._op(il, lhs, rhs)
        if result:
            il.append(self._lift_reg_mem(il, store=result))


class AluShiftRM(InstrHasModRegRM, InstrHasWidth, Instruction):
    def name(self):
        return instr_alu_shift[self._reg_bits()]

    def dst_reg(self):
        return self._reg2()

    def src_reg(self):
        if self.opcode & 0b10:
            return 'cl'
        else:
            return None

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += asm(
            ('reg', self.dst_reg()),
            ('opsep', ', ')
        )
        if self.src_reg():
            tokens += asm(('reg', self.src_reg()))
        else:
            tokens += asm(('int', '1', 1))
        return tokens

    def lift(self, il, addr):
        w = self.width()
        lhs = self._lift_reg_mem(il)
        rhs = il.reg(1, self.src_reg()) if self.src_reg() else il.const(1, 1)

        name = self.name()
        if name == 'rol':
            result = il.rotate_left(w, lhs, rhs, 'co')
        elif name == 'ror':
            result = il.rotate_right(w, lhs, rhs, 'co')
        elif name == 'rcl':
            result = il.rotate_left_carry(w, lhs, rhs, il.flag('c'), 'co')
        elif name == 'rcr':
            result = il.rotate_right_carry(w, lhs, rhs, il.flag('c'), 'co')
        elif name == 'shl':
            result = il.shift_left(w, lhs, rhs, 'co')
        elif name == 'shr':
            result = il.logical_shift_right(w, lhs, rhs, 'co')
        elif name == 'sar':
            result = il.arith_shift_right(w, lhs, rhs, '*')
        else:
            il.append(il.undefined())
            return
        il.append(self._lift_reg_mem(il, store=result))


class AluArithRegMem(InstrHasModRegRM, InstrHasWidth, Instruction):
    def name(self):
        return instr_alu_arith[self._reg_bits()]

    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += self._render_reg_mem()
        return tokens

    def lift(self, il, addr):
        w = self.width()
        name = self.name()
        if name == 'not':
            il.append(self._lift_reg_mem(il, store=il.not_expr(w, self._lift_reg_mem(il))))
        elif name == 'neg':
            il.append(self._lift_reg_mem(il, store=il.neg_expr(w, self._lift_reg_mem(il))))
        elif name in ('mul', 'imul'):
            accum  = il.reg(w, 'ax') if w == 2 else il.reg(w, 'al')
            # TODO: there's only one mult in LLIL, what gives?
            result = il.mult(w * 2, accum, self._lift_reg_mem(il))
            if w == 2:
                il.append(il.set_reg_split(w * 2, 'dx', 'ax', result))
            else:
                il.append(il.set_reg(w, 'ax', result))
        elif name in ('div', 'idiv'):
            dividend = il.reg_split(w * 2, 'dx', 'ax') if w == 2 else il.reg(w * 2, 'ax')
            divisor  = self._lift_reg_mem(il)
            if name == 'div':
                quotinent = il.div_unsigned(w, dividend, divisor)
                remainder = il.mod_unsigned(w, dividend, divisor)
            else:
                quotinent = il.div_signed(w, dividend, divisor)
                remainder = il.mod_signed(w, dividend, divisor)
            if w == 2:
                il.append(il.set_reg(w, 'ax', quotinent))
                il.append(il.set_reg(w, 'dx', remainder))
            else:
                il.append(il.set_reg(w, 'al', quotinent))
                il.append(il.set_reg(w, 'ah', remainder))
        else:
            il.append(il.undefined())
