import json
import pathlib

from ...          import Manager
from ...metaclass import Multiton
from ...errors.fe import FileOpenError                 as FOE
from ...errors.fe import FileWrongRequestedActionError as FWR

m = Manager()


class BaseFile(object):
    __metaclass__ = Multiton

    _IDENTIFIER   = 'name'

    def __init__(self, file_name, action):
        self.fname    = pathlib.Path(file_name)
        self.action   = action
        self._fd      = None
        self._pattern = None

    ##############
    # ATTRIBUTES #
    ##############
    @property
    def full(self):
        return str(self.fname.resolve())

    @property
    def dir(self):
        return str(self.fname.resolve().parent)

    @property
    def last_dir(self):
        return str(self.fname.resolve().parent.name)

    @property
    def name(self):
        return str(self.fname.name)

    @property
    def prefix(self):
        return str(self.fname.stem)

    @property
    def first_prefix(self):
        return self.name.split('.')[0]

    @property
    def extension(self):
        return str(self.fname.suffix)

    @property
    def extensions(self):
        return self.fname.suffixes

    @property
    def descriptor(self):
        return self._fd

    @property
    def size(self):
        return self.name.stat().st_size

    @property
    def pattern(self):
        if self._pattern is None:
            return None
        pattern = {}
        for p in self._pattern:
            pattern[p] = self.__dict__[p]
        return pattern

    ############
    # BOOLEANS #
    ############
    @property
    def is_open(self):
        return self._fd is not None

    @property
    def is_to_write(self):
        return self.action in set(['w', 'a'])

    @property
    def is_to_read(self):
        return self.action in set(['r'])

    ###########
    # METHODS #
    ###########
    def relative_to(self, path = pathlib.Path.cwd()):
        return self.fname.relative_to(path)

    ####################
    # METHODS: ON FILE #
    ####################
    def open(self):
        if self.is_open:
            return self
        self._fd = open(self.full, self.action)
        return self

    def read(self):
        self._check_action('r')
        return self._fd

    def readline(self):
        self._check_action('r')
        return self._fd.readline()

    def readJSON(self, encoding = 'utf-8'):
        d = []
        self.open()
        for l in self.read():
            d.append(l.strip())
        return json.loads(''.join(d), encoding=encoding)

    def write(self, line):
        self._check_action('w')
        self._fd.write(line)

    def flush(self):
        self._check_action('w')
        self._fd.flush()

    def close(self, clean = False):
        self._fd.close()
        self._fd = None

    ###################
    # PRIVATE METHODS #
    ###################
    def _check_action(self, call_method):
        if not self.is_open:
            raise FOE(self.full, self.action)
        if call_method == 'r' and self.is_to_write:
            raise FWR(self.full, self.action)
        elif call_method == 'w' and self.is_to_read:
            raise FWR(self.full, self.action)

    #################
    # CLASS METHODS #
    #################
    def __str__(self):
        return self.full

    def __repr__(self):
        cls = '.'.join([self.__class__.split('.')[0],
                        self.__class__.split('.')[-1]])
        return '<{0}: {1.full}>'.format(cls, self)
