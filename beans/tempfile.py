"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
from ..decorators import multiton

from . import Manager
from . import File
m = Manager()


@multiton
class TempFile(File):

    EMPTY_ACTION     = frozenset(['n'])
    WRITE_ACTION     = frozenset(['w', 'a', 'ar', 'wb'])
    AVAILABLE_ACTION = WRITE_ACTION.union(EMPTY_ACTION)

    ###################
    # PRIVATE METHODS #
    ###################
    def _register_file(self):
        m.add_tempfile(self.full)
