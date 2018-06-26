from binaryninja.lowlevelil import LowLevelILLabel

from ..helpers import *
from ..tables import *
from . import *
from .str import InstrString


__all__ = ['Repe', 'Repne']


class Rep(Prefix):
    def render(self, addr):
        tokens = Instruction.render(self, addr)
        tokens += self.next.render(addr + 1)
        return tokens

    def _zf_check(self):
        if not isinstance(self.next, InstrString):
            return None

        if self.next.base_name in ('movs', 'lods', 'stos'):
            return False
        elif self.next.base_name in ('cmps', 'scas'):
            return True

    def lift(self, il, addr):
        if not isinstance(self.next, InstrString):
            il.append(il.undefined())
            return

        # FIXME: doesn't seem to actually work
        preheader_instr = il.append(il.nop())
        df_values = il[preheader_instr].get_possible_flag_values('d')

        header_label = LowLevelILLabel()
        exit_label = LowLevelILLabel()

        il.mark_label(header_label)
        self.next.lift(il, addr + 1, df_values)

        il.append(il.set_reg(2, 'cx', il.sub(2, il.reg(2, 'cx'), il.const(2, 1))))
        cond = il.compare_equal(2, il.reg(2, 'cx'), il.const(2, 0))
        if self._zf_check():
            zf_cond = il.compare_equal(2, il.flag('z'), il.const(1, self._zf_cond))
            cond = il.or_expr(1, cond, zf_cond)
        il.append(il.if_expr(cond, header_label, exit_label))
        il.mark_label(exit_label)


class Repe(Rep):
    _zf_cond = 0

    def name(self):
        if self._zf_check():
            return 'repe'
        else:
            return 'rep'


class Repne(Rep):
    _zf_cond = 1

    def name(self):
        return 'repne'
