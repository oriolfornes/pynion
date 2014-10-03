"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import bz2
import filecmp
import gzip
import json
import os
import zipfile

from ..decorators import multiton
from ..           import errors

from . import Manager
m = Manager()


@multiton
class File(object):

    _IDENTIFIER      = 'name'
    _DESCRIPTOR      = 'simplefile.File'
    EMPTY_ACTION     = frozenset(['n'])
    WRITE_ACTION     = frozenset(['w', 'a', 'ar', 'wb'])
    READ_ACTION      = frozenset(['r', 'rb', 'r|*', 'r|'])
    AVAILABLE_ACTION = WRITE_ACTION.union(READ_ACTION, EMPTY_ACTION)

    ACTIVE_EXTENSIONS = {'.gz': 'gzip', '.bz2': 'bzip', '.zip': 'zip'}

    def __init__(self, name, action = 'r', auto_open = True, overwrite = None):

        self.name = name
        m.info('Opening: {0}'.format(self.full))

        # Determining the file type
        if not self.name.endswith(tuple(self.ACTIVE_EXTENSIONS.keys())):
            self._type = 'regular'
        else:
            for k in self.ACTIVE_EXTENSIONS.keys():
                if self.name.endswith(k):
                    self._type = self.ACTIVE_EXTENSIONS[k]
        m.detail('\tFile is {0}'.format(self._type))

        # The selected action must be valid according to the active extension
        # or simply to a regular file.
        self._action = None
        try:
            self._check_action(action.lower())
        except Exception as e:
            m.exception(str(e))
        m.debug('\tApply Action {0}'.format(self._action))

        # Local overwrite takes precedence over Global overwrite
        self._overwrite = m.evaluate_overwrite(overwrite)

        # Check that the requested action can be performed over that
        # particular file
        try:
            self._check_file()
        except Exception as e:
            m.exception(str(e))

        self._is_open = False
        self._fd      = None

        # For files generated via split
        self._section = None

        # Register the file
        self._register_file()

        # Set some limitations
        self._limitations()

        if auto_open:
            self.open()

    ##############
    # ATTRIBUTES #
    ##############
    @property
    def full(self):
        return os.path.abspath(self.name)

    @property
    def relative(self):
        return os.path.relpath(self.full)

    @property
    def dir(self):
        return os.path.split(self.full)[0]

    @property
    def lastdir(self):
        return os.path.basename(self.dir)

    @property
    def main(self):
        return os.path.basename(self.full)

    @property
    def prefix(self):
        return os.path.splitext(self.main)[0]

    @property
    def first_prefix(self):
        return self.main.split('.')[0]

    @property
    def extension(self):
        return os.path.splitext(self.main)[-1]

    @property
    def action(self):
        return self._action

    @property
    def descriptor(self):
        return self._fd

    @property
    def size(self):
        return os.path.getsize(self.full)

    @property
    def split_section(self):
        return self._section

    @split_section.setter
    def split_section(self, value):
        self._section = value

    ############
    # BOOLEANS #
    ############
    @property
    def is_regular_file(self):
        return self._type == 'regular'

    @property
    def is_compressed(self):
        return self.is_gzipped or self.is_zipped or self.is_bzipped

    @property
    def is_gzipped(self):
        return self._type.endswith('gzip')

    @property
    def is_zipped(self):
        return self._type == 'zip'

    @property
    def is_bzipped(self):
        return self._type.endswith('bzip')

    ###########
    # METHODS #
    ###########
    def open(self):
        if self._is_open:
            return

        if not self._action.startswith('r'):
            ostring = 'overwrite' if self._overwrite else 'not overwrite'
            m.debug('\tMode set to {0}'.format(ostring))

        self._is_open = True
        if self.is_regular_file:
            self._fd = open(self.full, self.action)
        if self.is_gzipped:
            self._fd = gzip.open(self.full, self.action)
        if self.is_bzipped:
            self._fd = bz2.BZ2File(self.full, self.action)
        if self.is_zipped:
            self._fd = zipfile.ZipFile(self.full)
            self._fd = self._fd.open(self._fd.namelist()[0])

    def read(self):
        self._work_action('r')
        return self._fd

    def readline(self):
        self._work_action('r')
        return self._fd.readline()

    def readJSON(self, encoding = 'utf-8'):
        d = []
        for l in self.read():
            d.append(l.strip())
        return json.loads(''.join(d), encoding=encoding)

    def write(self, line):
        self._work_action('w')
        self._fd.write(line)

    def flush(self):
        self._work_action('w')
        if self.is_bzipped:
            return
        self._fd.flush()

    def close(self, clean = False):
        self._fd.close()
        self._is_open = False

    def unregister(self):
        i = None
        for k in self.instances.keys():
            if k._DESCRIPTOR == File._DESCRIPTOR:
                i = k
                break
        del self.instances[i][getattr(self, self._IDENTIFIER)]

    def same_content(self, other):
        if isinstance(other, basestring):
            other = File(other)
        if not self.is_regular_file or not other.is_regular_file:
            raise errors.FileFunctionUnavailable(['same_content',
                                                  'compressed'])
        return filecmp.cmp(self.full, other.full)

    ###################
    # PRIVATE METHODS #
    ###################
    def _check_action(self, action):
        if not action in self.AVAILABLE_ACTION:
            raise errors.FileWrongActionError(action)

        if self.is_gzipped:
            if action.startswith('r'):
                action = 'rb'
            elif action.startswith('w'):
                action = 'wb'

        self._action = action

    def _work_action(self, action):
        if action == 'r':
            try:
                if not self._action in self.READ_ACTION:
                    raise errors.FileActionIsNotRead(self.full)
            except Exception as e:
                m.exception(str(e))
        elif action == 'w':
            try:
                if not self._action in self.WRITE_ACTION:
                    raise errors.FileActionIsNotWrite(self.full)
            except Exception as e:
                m.exception(str(e))

    def _check_file(self):
        if self._action.startswith('r'):
            if os.path.isdir(self.full):
                raise errors.FileIsDir(self.full)
            if not os.path.isfile(self.full):
                raise errors.FileNotExistsError(self.full)
            if not os.access(self.full, os.R_OK):
                raise errors.FileAccessError('read')
        if self._action.startswith('w') or self._action.startswith('a'):
            if os.path.isfile(self.full) and not self._overwrite:
                raise errors.FileOverwriteError(self.full)
            if not os.path.isdir(self.dir):
                raise errors.PathNotExistError(self.dir)
            if not os.access(self.dir, os.W_OK):
                raise errors.FileAccessError('write')

    def _register_file(self):
        m.experiment.files.add((self.full, self.action))

    def _limitations(self):
        if self._action in self.WRITE_ACTION:
            if self.is_bzipped:
                m.warning(['You are going to write a bzipped file',
                           'Though possible, we recommend to use gzipped files'])
            if self.is_zipped:
                m.exception(['As of now, writing ZIP files is not possible',
                             'We recommend the use of gzipped files'])

    #################
    # CLASS METHODS #
    #################
    def __str__(self):
        return self.full

    def __repr__(self):
        return self.full
