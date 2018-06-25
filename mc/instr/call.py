from binaryninja.enums import BranchType

from ..helpers import *
from ..tables import *
from . import *


__all__ = ['CallNearImm']


class Call(Instruction):
    def name(self):
        return 'call'


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
