import bz2
import gzip

from .basefile import BaseFile


class CompressedFile(BaseFile):

    def __init__(self, file_name, action, ctype):
        super(CompressedFile, self).__init__(file_name, action)
        self.ctype = ctype

    ############
    # BOOLEANS #
    ############
    @property
    def is_gzipped(self):
        return self.ctype == 'gzip'

    @property
    def is_bzipped(self):
        return self.ctype == 'bzip'

    ####################
    # METHODS: ON FILE #
    ####################
    def open(self):
        if self.is_open:
            return self
        if self.is_gzipped:
            self._fd = gzip.open(self.full, self.action)
        elif self.is_bzipped:
            self._fd = bz2.BZ2File(self.full, self.action)
        return self

    def flush(self):
        self._work_action('w')
        if self.is_bzipped:
            return
        self._fd.flush()
