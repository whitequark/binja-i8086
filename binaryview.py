from binaryninja import Architecture, Platform, BinaryView
from binaryninja.enums import SegmentFlag, SectionSemantics


__all__ = ['DosComBinaryView']


class DosComBinaryView(BinaryView):
    name = "COM"
    long_name = "DOS .COM Executable"

    @classmethod
    def is_valid_for_data(cls, data):
        # DOS .COM files don't have a proper header, but some other file formats
        # reuse the .COM extension, so we filter them out here.
        if not data.file.filename.lower().endswith('.com'):
            # Not a .COM file. (Duh.) You could still rename a .COM file into
            # (say) .FOO and add .FOO to COMSPEC, but then just rename it back
            # before analysis.
            return False

        if data.read(0, 2) == b'MZ':
            # It's an NE executable with a .COM filename.
            return False

        if data.read(0, 1) == b'\xc9':
            # It's a CP/M 3 executable with a .COM filename.
            # (Opcode C9 is RET on 8080 and LEAVE on 80186, so a COM file cannot
            # start with it.)
            return False

        # Now we know DOS will load this at 0x0100 and run with CS=DS=0x0000.
        return True

    def __init__(self, data):
        BinaryView.__init__(self, data.file, data)

        self.arch = Architecture['8086']
        self.platform = Platform['dos-8086']

    def init(self):
        data = self.parent_view

        seg_rw_  = (SegmentFlag.SegmentReadable |
                    SegmentFlag.SegmentWritable)
        seg_rwx  = (SegmentFlag.SegmentExecutable |
                    seg_rw_)
        seg_code = SegmentFlag.SegmentContainsCode
        seg_data = SegmentFlag.SegmentContainsData
        self.add_auto_segment(0x0100, len(data),
                              data.start, len(data),
                              seg_rwx|seg_code|seg_data)
        # self.add_auto_segment(self.end, 0x10000 - self.end,
        #                       len(data), 0,
        #                       seg_rw_|seg_data)

        sec_text = SectionSemantics.ReadOnlyCodeSectionSemantics
        sec_data = SectionSemantics.ReadWriteDataSectionSemantics
        self.add_auto_section('.text', 0x0100, len(data),
                              sec_text)
        self.add_auto_section('.data', 0x0100, len(data),
                              sec_data)

        self.navigate('Linear:COM', self.entry_point)

        return True

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return 0x0100

DosComBinaryView.register()
