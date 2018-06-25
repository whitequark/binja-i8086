from binaryninja import InstructionTextToken
from binaryninja.enums import InstructionTextTokenType


__all__  = ['fmt_dec', 'fmt_dec_sign',
            'fmtHex', 'fmt_hex2', 'fmt_hex4', 'fmt_hexW', 'fmt_hex_sign']
__all__ += ['fmt_imm', 'fmt_imm_sign', 'fmt_disp', 'fmt_code_rel', 'fmt_code_abs']
__all__ += ['token', 'asm']


def fmt_dec(value):
    return "{:d}".format(value)

def fmt_dec_sign(value):
    return "{:+d}".format(value)

def fmtHex(value):
    return "{:#x}".format(value)

def fmt_hex2(value):
    return "{:#02x}".format(value)

def fmt_hex4(value):
    return "{:#04x}".format(value)

def fmt_hexW(value, width):
    if width == 1:
        return fmt_hex2(value)
    elif width == 2:
        return fmt_hex4(value)
    else:
        raise ValueError('Invalid width {}'.format(width))

def fmt_hex_sign(value):
    return "{:+#x}".format(value)

def fmt_imm(value):
    if value < 256:
        return fmt_dec(value)
    else:
        return fmtHex(value)

def fmt_imm_sign(value):
    if abs(value) < 256:
        return fmt_dec_sign(value)
    else:
        return fmt_hex_sign(value)

def fmt_disp(value):
    return fmtHex(value)

def fmt_code_abs(value):
    return fmt_hex4(value)

def fmt_code_rel(value):
    return fmt_hex_sign(value)

def token(kind, text, *data):
    if kind == 'opcode':
        tokenType = InstructionTextTokenType.OpcodeToken
    elif kind == 'opsep':
        tokenType = InstructionTextTokenType.OperandSeparatorToken
    elif kind == 'instr':
        tokenType = InstructionTextTokenType.InstructionToken
    elif kind == 'text':
        tokenType = InstructionTextTokenType.TextToken
    elif kind == 'reg':
        tokenType = InstructionTextTokenType.RegisterToken
    elif kind == 'int':
        tokenType = InstructionTextTokenType.IntegerToken
    elif kind == 'addr':
        tokenType = InstructionTextTokenType.PossibleAddressToken
    elif kind == 'codeRelAddr':
        tokenType = InstructionTextTokenType.CodeRelativeAddressToken
    elif kind == 'beginMem':
        tokenType = InstructionTextTokenType.BeginMemoryOperandToken
    elif kind == 'endMem':
        tokenType = InstructionTextTokenType.EndMemoryOperandToken
    else:
        raise ValueError('Invalid token kind {}'.format(kind))
    return InstructionTextToken(tokenType, text, *data)

def asm(*parts):
    tokens = []
    for part in parts:
        tokens.append(token(*part))
    return tokens
