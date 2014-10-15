import os

import pathlib

from ..           import Manager
from ..errors.ffe import FileAccessError             as FAE
from ..errors.ffe import FileDirNotExistError        as FDN
from ..errors.ffe import FileIsDirError              as FID
from ..errors.ffe import FileNotExistsError          as FNE
from ..errors.ffe import FileOverwriteError          as FOE
from ..errors.ffe import FileWrongActionError        as FWA
from ..errors.ffe import FileWrongPatternIDError     as WPI
from ..errors.ffe import FileWrongPatternFormatError as WPF
from ._filetypes  import BaseFile, CompressedFile, ContainerFile

m = Manager()


class File(object):

    ACTIONS    = frozenset(['r', 'w', 'a', 't'])
    COMPRESSED = {'.gz':   'gzip',    '.bz2':     'bzip'}
    CONTAINER  = {'.tar':  'tar',     '.tgz':     'targzip', '.zip': 'zip',
                  '.tbz2': 'tarbzip', '.tar.gz':  'targzip',
                  '.tb2':  'tarbzip', '.tar.bz2': 'tarbzip'}

    def __new__(cls, file_name, action = 't',
                overwrite = None, temp = False, pattern = None):
        f = pathlib.Path(file_name)
        if f.is_dir():  # File is a directory
            raise FID(file_name, action)
        if action not in cls.ACTIONS:  # Wrong requested action for file
            raise FWA(file_name, action)
        if action == 't':  # TOUCH
            if f.is_file():
                m.info('{0} exists'.format(file_name))
            else:
                f.touch()
                m.info('{0} created'.format(file_name))
            return
        if action == 'w' or action == 'a':  # WRITE
            if f.is_file():  # Overwrite must be allowed if the file exists
                if not cls.M.evaluate_overwrite(overwrite):
                    raise FOE(file_name, action)
                if not os.access(f.resolve(), os.W_OK):
                    raise FAE(file_name, action)
            else:
                if not f.resolve().parent.exists():
                    raise FDN(str(f.resolve()), action)
                if not os.access(str(f.resolve().parent), os.W_OK):
                    raise FAE(str(f.resolve().parent), action)
        elif action == 'r':  # READ
            if not f.is_file():  # Read a file that does not exist
                raise FNE(file_name, action)
            if not os.access(str(f.resolve()), os.R_OK):
                raise FAE(file_name, action)
        if not temp:
            m.add_experiment_file(file_name, action)
        else:
            m.add_temporary_file(file_name)

        # Decide FileType
        sfxs = f.suffixes
        if sfxs[-1] in cls.CONTAINER:
            m.info('Declaring Container File: {0}'.format(file_name))
            newfile = ContainerFile(file_name, action + 'b',
                                    cls.CONTAINER[sfxs[-1]])
        elif len(sfxs) > 1 and '.'.join(sfxs[-2:]) in cls.CONTAINER:
            m.info('Declaring Container File: {0}'.format(file_name))
            newfile = ContainerFile(file_name, action,
                                    cls.CONTAINER[sfxs[-2:]])
        elif sfxs[-1] in cls.COMPRESSED:
            m.info('Declaring Compressed File: {0}'.format(file_name))
            newfile = CompressedFile(file_name, action + 'b',
                                     cls.COMPRESSED[sfxs[-1]])
        else:
            m.info('Declaring Regular File: {0}'.format(file_name))
            newfile = BaseFile(file_name, action)

        # Create FileName Pattern access
        if pattern is not None:
            fparts = f.name.split('.')
            pparts = pattern.split('.')
            if len(pparts) > len(fparts):
                raise WPF(file_name, pattern)
            classdefined = dir(newfile)
            print classdefined
            for i in range(len(pparts)):
                if pparts[i] not in classdefined:
                    newfile.__dict__[pparts[i]] = fparts[i]
                else:
                    raise WPI(file_name, pparts[i])
            newfile._pattern = pparts

        return newfile
