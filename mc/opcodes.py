__all__ = []


from .instr import Instruction
from .instr.seg import *
from .instr.alu import *
from .instr.inc_dec import *
from .instr.xchg import *
from .instr.test import *
from .instr.mov import *
from .instr.lea import *
from .instr.push_pop import *
from .instr.jmp import *
from .instr.call import *
from .instr.ret import *
from .instr.int import *
from .instr.cl_st import *
from .instr.in_out import *
from .instr.bad import *


Instruction.opcodes.update({
    # 0x00: AluLogicRMReg,
    # 0x01: AluLogicRMReg,
    0x02: AluLogicRegRM,
    0x03: AluLogicRegRM,
    0x04: AluLogicAccImm,
    0x05: AluLogicAccImm,
    0x06: PushSeg,
    0x07: PopSeg,
    # 0x08: AluLogicRMReg,
    # 0x09: AluLogicRMReg,
    0x0a: AluLogicRegRM,
    0x0b: AluLogicRegRM,
    0x0c: AluLogicAccImm,
    0x0d: AluLogicAccImm,
    0x0e: PushSeg,
    0x0f: Unassigned,
    # 0x10: AluLogicRMReg,
    # 0x11: AluLogicRMReg,
    0x12: AluLogicRegRM,
    0x13: AluLogicRegRM,
    0x14: AluLogicAccImm,
    0x15: AluLogicAccImm,
    0x16: PushSeg,
    0x17: PopSeg,
    # 0x18: AluLogicRMReg,
    # 0x19: AluLogicRMReg,
    0x1a: AluLogicRegRM,
    0x1b: AluLogicRegRM,
    0x1c: AluLogicAccImm,
    0x1d: AluLogicAccImm,
    0x1e: PushSeg,
    0x1f: PopSeg,
    # 0x20: AluLogicRMReg,
    # 0x21: AluLogicRMReg,
    0x22: AluLogicRegRM,
    0x23: AluLogicRegRM,
    0x24: AluLogicAccImm,
    0x25: AluLogicAccImm,
    0x26: Segment,
    # 0x27: Daa,
    # 0x28: AluLogicRMReg,
    # 0x29: AluLogicRMReg,
    0x2a: AluLogicRegRM,
    0x2b: AluLogicRegRM,
    0x2c: AluLogicAccImm,
    0x2d: AluLogicAccImm,
    0x2e: Segment,
    # 0x2f: Das,
    # 0x30: AluLogicRMReg,
    # 0x31: AluLogicRMReg,
    0x32: AluLogicRegRM,
    0x33: AluLogicRegRM,
    0x34: AluLogicAccImm,
    0x35: AluLogicAccImm,
    0x36: Segment,
    # 0x37: Aaa,
    # 0x38: AluLogicRMReg,
    # 0x39: AluLogicRMReg,
    0x3a: AluLogicRegRM,
    0x3b: AluLogicRegRM,
    0x3c: AluLogicAccImm,
    0x3d: AluLogicAccImm,
    0x3e: Segment,
    # 0x3f: Aas,
    0x40: IncDecReg,
    0x41: IncDecReg,
    0x42: IncDecReg,
    0x43: IncDecReg,
    0x44: IncDecReg,
    0x45: IncDecReg,
    0x46: IncDecReg,
    0x47: IncDecReg,
    0x48: IncDecReg,
    0x49: IncDecReg,
    0x4a: IncDecReg,
    0x4b: IncDecReg,
    0x4c: IncDecReg,
    0x4d: IncDecReg,
    0x4e: IncDecReg,
    0x4f: IncDecReg,
    0x50: PushReg,
    0x51: PushReg,
    0x52: PushReg,
    0x53: PushReg,
    0x54: PushReg,
    0x55: PushReg,
    0x56: PushReg,
    0x57: PushReg,
    0x58: PopReg,
    0x59: PopReg,
    0x5a: PopReg,
    0x5b: PopReg,
    0x5c: PopReg,
    0x5d: PopReg,
    0x5e: PopReg,
    0x5f: PopReg,
    0x60: Unassigned,
    0x61: Unassigned,
    0x62: Unassigned,
    0x63: Unassigned,
    0x64: Unassigned,
    0x65: Unassigned,
    0x66: Unassigned,
    0x67: Unassigned,
    0x68: Unassigned,
    0x69: Unassigned,
    0x6a: Unassigned,
    0x6b: Unassigned,
    0x6c: Unassigned,
    0x6d: Unassigned,
    0x6e: Unassigned,
    0x6f: Unassigned,
    0x70: JmpCond,
    0x71: JmpCond,
    0x72: JmpCond,
    0x73: JmpCond,
    0x74: JmpCond,
    0x75: JmpCond,
    0x76: JmpCond,
    0x77: JmpCond,
    0x78: JmpCond,
    0x79: JmpCond,
    0x7a: JmpCond,
    0x7b: JmpCond,
    0x7c: JmpCond,
    0x7d: JmpCond,
    0x7e: JmpCond,
    0x7f: JmpCond,
    0x80: AluLogicRMImm,
    0x81: AluLogicRMImm,
    0x82: AluLogicRMImm,
    0x83: AluLogicRMImm,
    # 0x84: TestRMReg,
    # 0x85: TestRMReg,
    # 0x86: XchgRegRM,
    # 0x87: XchgRegRM,
    0x88: MovRMReg,
    0x89: MovRMReg,
    0x8a: MovRegRM,
    0x8b: MovRegRM,
    0x8c: MovRMSeg,
    0x8d: Lea,
    0x8e: MovSegRM,
    # 0x8f: PopRM,
    0x90: Nop,
    0x91: Xchg,
    0x92: Xchg,
    0x93: Xchg,
    0x94: Xchg,
    0x95: Xchg,
    0x96: Xchg,
    0x97: Xchg,
    # 0x98: Cbw,
    # 0x99: Cwd,
    # 0x9a: CallFarImm,
    # 0x9b: Wait,
    # 0x9c: Pushf,
    # 0x9d: Popf,
    # 0x9e: Sahf,
    # 0x9f: Lahf,
    0xa0: MovAccMem,
    0xa1: MovAccMem,
    0xa2: MovMemAcc,
    0xa3: MovMemAcc,
    # 0xa4: Movs,
    # 0xa5: Movs,
    # 0xa6: Cmps,
    # 0xa7: Cmps,
    0xa8: TestAccImm,
    0xa9: TestAccImm,
    # 0xaa: Stos,
    # 0xab: Stos,
    # 0xac: Lods,
    # 0xad: Lods,
    # 0xae: Scas,
    # 0xaf: Scas,
    0xb0: MovRegImm,
    0xb1: MovRegImm,
    0xb2: MovRegImm,
    0xb3: MovRegImm,
    0xb4: MovRegImm,
    0xb5: MovRegImm,
    0xb6: MovRegImm,
    0xb7: MovRegImm,
    0xb8: MovRegImm,
    0xb9: MovRegImm,
    0xba: MovRegImm,
    0xbb: MovRegImm,
    0xbc: MovRegImm,
    0xbd: MovRegImm,
    0xbe: MovRegImm,
    0xbf: MovRegImm,
    0xc0: Unassigned,
    0xc1: Unassigned,
    0xc2: RetNearImm,
    0xc3: RetNear,
    # 0xc4: Les,
    # 0xc5: Lds,
    0xc6: MovMemImm,
    0xc7: MovMemImm,
    0xc8: Unassigned,
    0xc9: Unassigned,
    # 0xca: RetFarImm,
    # 0xcb: RetImm,
    0xcc: Int3,
    0xcd: IntImm,
    # 0xce: Into,
    # 0xcf: Iret,
    0xd0: AluShiftRM,
    0xd1: AluShiftRM,
    0xd2: AluShiftRM,
    0xd3: AluShiftRM,
    # 0xd4: Aam,
    # 0xd5: Aad,
    0xd6: Unassigned,
    # 0xd7: Xlat,
    0xd8: UnassignedRM,
    0xd9: UnassignedRM,
    0xda: UnassignedRM,
    0xdb: UnassignedRM,
    0xdc: UnassignedRM,
    0xdd: UnassignedRM,
    0xde: UnassignedRM,
    0xdf: UnassignedRM,
    0xe0: Loopne,
    0xe1: Loope,
    0xe2: Loop,
    0xe3: Jcxz,
    0xe4: InImm,
    0xe5: InImm,
    0xe6: OutImm,
    0xe7: OutImm,
    0xe8: CallNearImm,
    0xe9: JmpNearImm,
    0xea: JmpFarImm,
    0xeb: JmpShort,
    0xec: InReg,
    0xed: InReg,
    0xee: OutReg,
    0xef: OutReg,
    # 0xf0: Lock,
    0xf1: Unassigned,
    # 0xf2: Repne,
    # 0xf3: Rep,
    # 0xf4: Hlt,
    0xf5: Cmc,
    0xf6: {
        0b000: TestRegMemImm,
        0b001: UnassignedRM,
        0b010: AluArithRegMem,
        0b011: AluArithRegMem,
        0b100: AluArithRegMem,
        0b101: AluArithRegMem,
        0b110: AluArithRegMem,
        0b111: AluArithRegMem,
    },
    0xf7: {
        0b000: TestRegMemImm,
        0b001: UnassignedRM,
        0b010: AluArithRegMem,
        0b011: AluArithRegMem,
        0b100: AluArithRegMem,
        0b101: AluArithRegMem,
        0b110: AluArithRegMem,
        0b111: AluArithRegMem,
    },
    0xf8: Clc,
    0xf9: Stc,
    0xfa: Cli,
    0xfb: Sti,
    0xfc: Cld,
    0xfd: Std,
    0xfe: {
        0b000: IncDecRM,
        0b001: IncDecRM,
        0b010: UnassignedRM,
        0b011: UnassignedRM,
        0b100: UnassignedRM,
        0b101: UnassignedRM,
        0b110: UnassignedRM,
        0b111: UnassignedRM,
    },
    0xff: {
        0b000: IncDecRM,
        0b001: IncDecRM,
        # 0b010: CallNearRM,
        # 0b011: CallFarMem,
        0b100: JmpNearRM,
        0b101: JmpFarMem,
        0b111: UnassignedRM,
    }
})