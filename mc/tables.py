from binaryninja.enums import LowLevelILFlagCondition


__all__  = ['reg8', 'reg16', 'reg_seg', 'regs_rm', 'flags_bits']
__all__ += ['op_width']
__all__ += ['instr_alu_logic', 'instr_alu_arith', 'instr_alu_shift',
            'instr_jump', 'jump_cond', 'instr_loop']


# Register tables
reg8 = {
    0b000: 'al',
    0b001: 'cl',
    0b010: 'dl',
    0b011: 'bl',
    0b100: 'ah',
    0b101: 'ch',
    0b110: 'dh',
    0b111: 'bh'
}

reg16 = {
    0b000: 'ax',
    0b001: 'cx',
    0b010: 'dx',
    0b011: 'bx',
    0b100: 'sp',
    0b101: 'bp',
    0b110: 'si',
    0b111: 'di'
}

reg_seg = {
    0b00: 'es',
    0b01: 'cs',
    0b10: 'ss',
    0b11: 'ds'
}

regs_rm = {
    0b000: ['bx', 'si'],
    0b001: ['bx', 'di'],
    0b010: ['bp', 'si'],
    0b011: ['bp', 'di'],
    0b100: ['si'],
    0b101: ['di'],
    0b110: ['bp'],
    0b111: ['bx']
}

flags_bits = [
    ('c', 0),
    ('p', 2),
    ('a', 4),
    ('z', 6),
    ('s', 7),
    ('i', 9),
    ('d', 10),
    ('o', 11),
]


# Operator tables
op_width = {
    0b0: 'byte',
    0b1: 'word'
}


# Instruction tables
instr_alu_logic = {
    0b000: 'add',
    0b001: 'or',
    0b010: 'adc',
    0b011: 'sbb',
    0b100: 'and',
    0b101: 'sub',
    0b110: 'xor',
    0b111: 'cmp'
}

instr_alu_arith = {
    0b000: 'test',
    0b001: 'illegal',
    0b010: 'not',
    0b011: 'neg',
    0b100: 'mul',
    0b101: 'imul',
    0b110: 'div',
    0b111: 'idiv'
}

instr_alu_shift = {
    0b000: 'rol',
    0b001: 'ror',
    0b010: 'rcl',
    0b011: 'rcr',
    0b100: 'shl',
    0b101: 'shr',
    0b110: 'illegal',
    0b111: 'sar'
}

instr_jump = {
    0b0000: 'jo',
    0b0001: 'jno',
    0b0010: 'jb',   # /jc/jb
    0b0011: 'jae',  # /jnc/jae
    0b0100: 'je',   # /jz
    0b0101: 'jne',  # /jnz
    0b0110: 'jbe',  # /jbe
    0b0111: 'ja',   # /ja
    0b1000: 'js',
    0b1001: 'jns',
    0b1010: 'jpe',  # /jp
    0b1011: 'jpo',  # /jnp
    0b1100: 'jl',   # /jnge
    0b1101: 'jge',  # /jnl
    0b1110: 'jle',  # /jng
    0b1111: 'jg'    # /jnle
}

jump_cond = {
    'jo':  LowLevelILFlagCondition.LLFC_O,
    'jno': LowLevelILFlagCondition.LLFC_NO,
    'jb':  LowLevelILFlagCondition.LLFC_ULT,
    'jae': LowLevelILFlagCondition.LLFC_UGE,
    'je':  LowLevelILFlagCondition.LLFC_E,
    'jne': LowLevelILFlagCondition.LLFC_NE,
    'jbe': LowLevelILFlagCondition.LLFC_ULE,
    'ja':  LowLevelILFlagCondition.LLFC_UGT,
    'js':  LowLevelILFlagCondition.LLFC_NEG,
    'jns': LowLevelILFlagCondition.LLFC_POS,
    'jl':  LowLevelILFlagCondition.LLFC_SLT,
    'jge': LowLevelILFlagCondition.LLFC_SGE,
    'jle': LowLevelILFlagCondition.LLFC_SLE,
    'jg':  LowLevelILFlagCondition.LLFC_SGT
}

instr_loop = {
    0b00: 'loopne',
    0b01: 'loope',
    0b10: 'loop',
    0b11: 'jcxz'
}
