from binaryninja import Architecture, Platform


__all__ = ['Dos']


class Dos(Platform):
    name = 'dos-8086'


arch = Architecture['8086']

dos = Dos(arch)
dos.default_calling_convention = arch.calling_conventions['default']
dos.cdecl_calling_convention = arch.calling_conventions['cdecl']
dos.register('dos')
