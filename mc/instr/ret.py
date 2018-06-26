from binaryninja.enums import BranchType

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['RetNear', 'RetNearImm', 'RetFar', 'RetFarImm']


class Ret(Instruction):
    def name(self):
        if self.opcode & 0b1000:
            return 'retf'
        else:
            return 'ret'

    def analyze(self, info, addr):
        Instruction.analyze(self, info, addr)
        info.add_branch(BranchType.FunctionReturn)


class RetImm(InstrHasImm, Ret):
    def width(self):
        return 2

    def render(self, addr):
        tokens = Ret.render(addr)
        tokens += [
            ('int', fmt_hex2(self.imm), self.imm),
        ]
        return tokens


class RetFar(Ret):
    def lift(self, il, addr):
        ip = il.pop(2)
        cs = il.pop(2)
        il.append(il.ret(self._lift_phys_addr(il, cs, ip)))


class RetFarImm(RetImm):
    def lift(self, il, addr):
        ip = il.pop(2)
        cs = il.pop(2)
        il.append(il.set_reg(2, 'sp', il.add(2, il.reg(2, 'sp'), il.const(2, self.imm))))
        il.append(il.ret(self._lift_phys_addr(il, cs, ip)))


class RetNear(Ret):
    def lift(self, il, addr):
        ip = il.pop(2)
        il.append(il.ret(ip))


class RetNearImm(RetImm):
    def lift(self, il, addr):
        ip = il.pop(2)
        il.append(il.set_reg(2, 'sp', il.add(2, il.reg(2, 'sp'), il.const(2, self.imm))))
        il.append(il.ret(ip))
