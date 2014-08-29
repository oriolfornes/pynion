class DecoratorError(Exception):
    def __init__(self, info):
        self.info = info


class DecoratorErrorBadMultitonIdentifier(DecoratorError):
    def __str__(self):
        data = ['{0.info[0]} probably is not a good identifier to distinguish',
                'multitones of {0.info[1]}. It might possible not even be',
                'one of the __init__ parameters of the object.',
                'Re-check your object definition.']
        return ' '.join(data).format(self).replace('. ', '.\n')


class FileError(Exception):
    def __init__(self, info):
        self.info = info


class FileNotExistsError(FileError):
    def __str__(self):
        return '{0.info} does not exist'.format(self)


class FileOverwriteError(FileError):
    def __str__(self):
        return '{0.info} already exists'.format(self)


class FileAccessError(FileError):
    def __str__(self):
        return 'Access to {0.info} not allowed'.format(self)


class FileWrongActionError(FileError):
    def __str__(self):
        return '{0.info} is not an acceptable action for File'.format(self)


class FileIsDir(FileError):
    def __str__(self):
        return '{0.info} is a directory'.format(self)


class FileActionIsNotRead(FileError):
    def __str__(self):
        return '{0.info} is not open to read'.format(self)


class FileActionIsNotWrite(FileError):
    def __str__(self):
        return '{0.info} is not open to write'.format(self)


class FileFunctionUnavailable(FileError):
    def __str__(self):
        return '{0.info[0]} is unavailable for {0.info[1]} files'.format(self)


class FileContainerFileNotFoud(FileError):
    def __str(self):
        return '{0.info[0]} cannot be found in {0.info[1]}'.format(self)


class PathError(Exception):
    def __init__(self, info):
        self.info = info


class PathNotExistError(PathError):
    def __str__(self):
        return 'Directory {0.info} does not exist'.format(self)


class PathActionInvalid(PathError):
    def __str__(self):
        return 'Action {0.info[0]} not allowed in {0.info[1]}'.format(self)
