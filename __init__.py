from binaryninja import log, Architecture, RegisterInfo, IntrinsicInfo, InstructionInfo
from binaryninja.enums import Endianness, FlagRole, LowLevelILFlagCondition
from binaryninja.types import Type

from . import mc


class Intel8086(Architecture):
    name = "8086"
    endianness = Endianness.LittleEndian

    default_int_size = 2
    address_size = 3

    stack_pointer = 'sp'
    regs = {
        # General
        'ax': RegisterInfo('ax', 2, 0),
            'al': RegisterInfo('ax', 1, 0),
            'ah': RegisterInfo('ax', 1, 1),
        'cx': RegisterInfo('cx', 2, 0),
            'cl': RegisterInfo('cx', 1, 0),
            'ch': RegisterInfo('cx', 1, 1),
        'bx': RegisterInfo('bx', 2, 0),
            'bl': RegisterInfo('bx', 1, 0),
            'bh': RegisterInfo('bx', 1, 1),
        'dx': RegisterInfo('dx', 2, 0),
            'dl': RegisterInfo('dx', 1, 0),
            'dh': RegisterInfo('dx', 1, 1),
        'sp': RegisterInfo('sp', 2),
        'bp': RegisterInfo('bp', 2),
        'si': RegisterInfo('si', 2),
        'di': RegisterInfo('di', 2),
        # Segment
        'cs': RegisterInfo('cs', 2),
        'ds': RegisterInfo('ds', 2),
        'es': RegisterInfo('es', 2),
        'ss': RegisterInfo('ss', 2),
        # Instruction pointer
        'ip': RegisterInfo('ip', 2)
    }
    flags = [
        # Status
        'c', # carry
        'p', # parity
        'a', # aux carry
        'z', # zero
        's', # sign
        'o', # overflow
        # Control
        'i', # interrupt
        'd', # direction
        't', # trap
    ]
    flag_roles = {
        'c': FlagRole.CarryFlagRole,
        'p': FlagRole.OddParityFlagRole,
        'a': FlagRole.HalfCarryFlagRole,
        'z': FlagRole.ZeroFlagRole,
        's': FlagRole.NegativeSignFlagRole,
        't': FlagRole.SpecialFlagRole,
        'i': FlagRole.SpecialFlagRole,
        'd': FlagRole.SpecialFlagRole,
        'o': FlagRole.OverflowFlagRole,
    }
    flag_write_types = [
        '',
        '*',
        '!c',
        'co',
    ]
    flags_written_by_flag_write_type = {
        '*':  ['c', 'p', 'a', 'z', 's', 'o'],
        '!c': ['p', 'a', 'z', 's', 'o'],
        'co': ['c', 'o'],
    }
    flags_required_for_flag_condition = {
        LowLevelILFlagCondition.LLFC_E:   ['z'],
        LowLevelILFlagCondition.LLFC_NE:  ['z'],
        LowLevelILFlagCondition.LLFC_SLT: ['s', 'o'],
        LowLevelILFlagCondition.LLFC_ULT: ['c'],
        LowLevelILFlagCondition.LLFC_SLE: ['z', 's', 'o'],
        LowLevelILFlagCondition.LLFC_ULE: ['c', 'z'],
        LowLevelILFlagCondition.LLFC_SGE: ['s', 'o'],
        LowLevelILFlagCondition.LLFC_UGE: ['c'],
        LowLevelILFlagCondition.LLFC_SGT: ['z', 's', 'o'],
        LowLevelILFlagCondition.LLFC_UGT: ['c', 'z'],
        LowLevelILFlagCondition.LLFC_NEG: ['s'],
        LowLevelILFlagCondition.LLFC_POS: ['s'],
        LowLevelILFlagCondition.LLFC_O:   ['o'],
        LowLevelILFlagCondition.LLFC_NO:  ['o'],
    }

    intrinsics = {
        'outb': IntrinsicInfo([Type.int(2), Type.int(1)], []),
        'outw': IntrinsicInfo([Type.int(2), Type.int(2)], []),
        'inb': IntrinsicInfo([Type.int(1)], [Type.int(2)]),
        'inw': IntrinsicInfo([Type.int(2)], [Type.int(2)]),
    }

    def get_instruction_info(self, data, addr):
        decoded = mc.decode(data, addr)
        if decoded:
            info = InstructionInfo()
            decoded.analyze(info, addr)
            return info

    def get_instruction_text(self, data, addr):
        decoded = mc.decode(data, addr)
        if decoded:
            encoded = data[:decoded.total_length()]
            recoded = mc.encode(decoded, addr)
            if encoded != recoded:
                log.log_error("Instruction roundtrip error")
                log.log_error("".join([str(x) for x in decoded.render(addr)]))
                log.log_error("Orig: {}".format(encoded.encode('hex')))
                log.log_error("New:  {}".format(recoded.encode('hex')))

            return decoded.render(addr), decoded.total_length()

    def get_instruction_low_level_il(self, data, addr, il):
        decoded = mc.decode(data, addr)
        if decoded:
            decoded.lift(il, addr)
            return decoded.total_length()

    def convert_to_nop(self, data, addr):
        return b'\x90' * len(data)

    def is_always_branch_patch_available(self, data, addr):
        decoded = mc.decode(data, addr)
        if decoded:
            return isinstance(decoded, mc.instr.jmp.JmpCond)

    def always_branch(self, data, addr):
        branch = mc.decode(data, addr)
        branch = branch.to_always()
        return mc.encode(branch, addr)

    def is_invert_branch_patch_available(self, data, addr):
        decoded = mc.decode(data, addr)
        if decoded:
            return isinstance(decoded, mc.instr.jmp.JmpCond)

    def invert_branch(self, data, addr):
        branch = mc.decode(data, addr)
        branch = branch.to_inverted()
        return mc.encode(branch, addr)

Intel8086.register()
