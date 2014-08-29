"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import os
import tarfile
import zipfile

from ..decorators import multiton
from ..           import errors

from . import Manager
from . import File
m = Manager()


@multiton
class ContainerFile(File):

    EMPTY_ACTION     = frozenset(['n'])
    READ_ACTION      = frozenset(['r', 'rb', 'r|*', 'r|'])
    AVAILABLE_ACTION = READ_ACTION.union(EMPTY_ACTION)

    ACTIVE_EXTENSIONS = {'.tar':     'tar',     '.tgz':    'targzip',
                         '.tbz2':    'tarbzip', '.tar.gz': 'targzip',
                         '.tar.bz2': 'tarbzip', '.zip':    'zip',
                         '.tb2':     'tarbzip'}

    def __init__(self, name, action = 'r', overwrite = None):
        File.__init__(self, name, action, overwrite)
        self._len = None

    ############
    # BOOLEANS #
    ############
    @property
    def is_tarfile(self):
        '''
        @return:  {Boolean}
        '''
        return self._type.startswith('tar')

    ###########
    # METHODS #
    ###########
    def open(self):
        if self._is_open:
            return

        self._is_open = True
        if self.is_tarfile:
            self._fd = tarfile.open(self.full)
        if self.is_zipped:
            self._fd = zipfile.ZipFile(self.full)

    def read_file(self, file_name):
        if self.is_zipped:
            if file_name not in self._fd.namelist():
                raise errors.FileContainerFileNotFoud([file_name, self.full])
            return self._fd.read(file_name).split('\n')
        if self.is_tarfile:
            if file_name not in self._fd.getnames():
                raise errors.FileContainerFileNotFoud([file_name, self.full])
            return self._fd.extractfile(self._fd.getmember(file_name)).readlines()

    def has_file(self, file_name):
        if self.is_zipped:
            return file_name in self._fd.namelist()
        if self.is_tarfile:
            return file_name in self._fd.getnames()

    def extract(self, target_dir = os.getcwd()):
        if not os.path.isdir(target_dir) or not os.access(target_dir, os.W_OK):
            raise errors.PathActionInvalid(['write', target_dir])
        self._fd.extractall(path = target_dir)

    def list_files(self):
        if self.is_tarfile:
            return self._fd.getnames()
        if self.is_zipped:
            return self._fd.namelist()

    ###################
    # PRIVATE METHODS #
    ###################
    def _check_action(self, action):
        if not action in self.AVAILABLE_ACTION:
            raise errors.FileWrongActionError(action)

        if self.is_gzipped:
            if action.startswith('r'):
                action = 'rb'

        self._action = action

    #################
    # CLASS METHODS #
    #################
    def __len__(self):
        if self._len is None:
            if self.is_tarfile:
                tar       = tarfile.open(self.full)
                self._len = len(tar.getmembers())
            if self.is_zipped:
                zzip      = zipfile.ZipFile(self.full)
                self._len = len(zzip.namelist())
        return self._len
