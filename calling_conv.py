from binaryninja import Architecture, CallingConvention


__all__ = ['Intel8086CallingConvention',
           'CdeclCallingConvention',
           'PascalCallingConvention']


class Intel8086CallingConvention(CallingConvention):
    caller_saved_regs = ['ax', 'bx', 'cx', 'dx', 'es']
    int_arg_regs = []
    int_return_reg = 'ax'
    high_int_return_reg = 'dx'


class CdeclCallingConvention(Intel8086CallingConvention):
    stack_adjusted_on_return = False


class PascalCallingConvention(Intel8086CallingConvention):
    stack_adjusted_on_return = True


arch = Architecture['8086']
arch.register_calling_convention(Intel8086CallingConvention(arch, 'default'))
arch.register_calling_convention(CdeclCallingConvention(arch, 'cdecl'))
arch.register_calling_convention(PascalCallingConvention(arch, 'pascal'))
