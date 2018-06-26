from binaryninja.enums import RegisterValueType
from binaryninja.lowlevelil import LowLevelILLabel, LowLevelILOperation

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['Movs', 'Cmps', 'Stos', 'Lods', 'Scas']


class InstrString(InstrHasWidth, Instruction):
    default_segment = 'ds'

    def name(self):
        if self.width() == 2:
            return self.base_name + 'w'
        else:
            return self.base_name + 'b'

    def _lift_inc_dec(self, il, regs, df_values):
        if not isinstance(regs, tuple):
            regs = (regs,)

        if df_values is not None and df_values.type == RegisterValueType.ConstantValue:
            if df_values.value:
                for reg in regs:
                    il.append(il.set_reg(2, reg, il.sub(2, il.reg(2, reg), il.const(2, 1))))
            else:
                for reg in regs:
                    il.append(il.set_reg(2, reg, il.add(2, il.reg(2, reg), il.const(2, 1))))
        else:
            inc_label, dec_label = LowLevelILLabel(), LowLevelILLabel()
            post_label = LowLevelILLabel()
            il.append(il.if_expr(il.flag('d'), dec_label, inc_label))
            il.mark_label(inc_label)
            for reg in regs:
                il.append(il.set_reg(2, reg, il.add(2, il.reg(2, reg), il.const(2, 1))))
            il.append(il.goto(post_label))
            il.mark_label(dec_label)
            for reg in regs:
                il.append(il.set_reg(2, reg, il.sub(2, il.reg(2, reg), il.const(2, 1))))
            il.append(il.goto(post_label))
            il.mark_label(post_label)


class Movs(InstrHasSegment, InstrString):
    base_name = 'movs'

    def lift(self, il, addr, df_values=None):
        w = self.width()
        value = il.load(w, self._lift_addr(il, self.segment(), 'si'))
        il.append(il.store(w, self._lift_addr(il, 'es', 'di'), value))
        self._lift_inc_dec(il, ('si', 'di'), df_values)


class Cmps(InstrHasSegment, InstrString):
    base_name = 'cmps'

    def lift(self, il, addr, df_values=None):
        w = self.width()
        il.append(il.sub(w, il.load(w, self._lift_addr(il, self.segment(), 'si')),
                            il.load(w, self._lift_addr(il, 'es', 'di')), '*'))
        self._lift_inc_dec(il, ('si', 'di'), df_values)


class Stos(InstrString):
    base_name = 'stos'

    def lift(self, il, addr, df_values=None):
        w = self.width()
        il.append(il.store(w, self._lift_addr(il, 'es', 'di'), il.reg(w, 'ax')))
        self._lift_inc_dec(il, 'di', df_values)


class Lods(InstrHasSegment, InstrString):
    base_name = 'lods'

    def lift(self, il, addr, df_values=None):
        w = self.width()
        il.append(il.set_reg(w, 'ax', il.load(w, self._lift_addr(il, self.segment(), 'si'))))
        self._lift_inc_dec(il, 'si', df_values)


class Scas(InstrString):
    base_name = 'scas'

    def lift(self, il, addr, df_values=None):
        w = self.width()
        il.append(il.sub(w, 'ax', il.load(w, self._lift_addr(il, 'es', 'di')), '*'))
        self._lift_inc_dec(il, 'di', df_values)
