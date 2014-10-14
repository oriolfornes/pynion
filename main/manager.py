"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import atexit
import ConfigParser
import datetime
import inspect
import json
import logging
import os
import sys
import time
import traceback
import warnings

from ..metaclass  import Singleton
from ._inner      import Project
from ._inner      import Experiment


class Manager(object):

    __metaclass__ = Singleton

    _GENERAL_FORMAT = '%(asctime)s - %(levelname)-7.7s - %(message)s'
    _TIME_FORMAT    = '%Y-%m-%d %H:%M'
    _FRMT           = logging.Formatter(_GENERAL_FORMAT, _TIME_FORMAT)
    _MSSG           = '[ {0} ] - {1}'

    def __init__(self):
        # Logger parameters: Level of detail
        self._verbose = False  # Requires setter
        self._debug   = False  # Requires setter
        self._detail  = False  # Requires setter

        # Management parameters:
        self._tempfiles = set()  # Requires setter
        self._clean     = True   # Clean the temporary files

        # IO conditions:
        self._overwrite = False  # Requires setter

        # Create a logger.
        # Null handler is added so that if no handler is active
        # warnings and errors will not display a 'handler not found' message
        self._fd = logging.getLogger(__name__)
        self._fd.setLevel(logging.DEBUG)
        self._fd.addHandler(logging.NullHandler())

        # Project and Experiment
        rfname, cfname, pfname = self._configuration()
        self.project = Project(rfname, cfname, pfname)
        try:
            self.experiment = Experiment()
        except:
            self.exception(['Bash command could not be imported.',
                            'System needs to be UNIX based'])

        # Register function to execute at exit
        atexit.register(self.shutdown)
        atexit.register(self.cleanup)

    ####################
    # METHODS: SETTERS #
    ####################
    def set_verbose(self):
        self._verbose = True

    def set_debug(self):
        self.set_verbose()
        self._debug  = True

    def set_detail(self):
        self._detail = True
        self.set_unclean()
        self.set_debug()

    def set_unclean(self):
        self._clean = False

    def set_stdout(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self._FRMT)
        self._fd.addHandler(handler)
        self.info('Active STDOUT')

    def set_overwrite(self):
        self._overwrite = True

    def set_logfile(self, logname = os.getcwd()):
        if os.path.isdir(logname):
            script_name = os.path.split(os.path.splitext(sys.argv[0])[0])[1]
            if script_name == '__main__':
                script_name = os.path.split(os.path.split(sys.argv[0])[0])[1]
            log_file    = ".".join([script_name, str(os.getpid()), 'log'])
            logname     = os.path.join(logname, log_file)

        self.info('LOGfile: {0}'.format(logname))
        handler = logging.FileHandler(filename = logname,
                                      encoding = 'utf8')
        handler.setFormatter(self._FRMT)
        self._fd.addHandler(handler)

    ###########
    # METHODS #
    ###########
    def add_temporary_file(self, tempfile):
        self.info('Registering temporary file {0}'.format(tempfile))
        self._tempfiles.add(tempfile)

    def add_experiment_file(self, filename, action):
        self.experiment.add_file(filename, action)

    def countdown(self, max_time):
        t  = str(datetime.timedelta(seconds=max_time))
        n  = time.localtime()
        s1 = 'Waiting for: {0} hours'.format(t)
        s2 = 'Wait started at {0}'.format(time.strftime('%X', n))
        s3 = 'on {0}'.format(time.strftime('%Y-%m-%d', n))
        sys.stderr.write('{0}\t{1} {2}\n\n'.format(s1, s2, s3))
        while max_time > 0:
            t = str(datetime.timedelta(seconds=max_time))
            sys.stderr.write('Remaining: {0} hours'.format(t))
            time.sleep(1)
            max_time -= 1
            if bool(max_time):
                sys.stderr.write('\r')
            else:
                sys.stderr.write('\r')
                t = str(datetime.timedelta(seconds=max_time))
                sys.stderr.write('Remaining: {0} hours'.format(t))
                sys.stderr.write('\n')

    def evaluate_overwrite(self, overwrite):
        return self._overwrite if overwrite is None else overwrite

    ####################
    # METHODS: LOGGING #
    ####################
    def info(self, mssg):
        if not self._verbose:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.info(line)

    def debug(self, mssg):
        if not self._debug:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.debug(line)

    def detail(self, mssg):
        if not self._detail:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.debug(line)

    def warning(self, mssg):
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            # If we have no handler added, we warn through the warnings module
            if len(self._fd.handlers) > 1:
                self._fd.warning(line)
            else:
                warnings.warn(line + '\n')

    def exception(self, mssg):
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            if len(self._fd.handlers) > 1:
                self._fd.exception(line)
            else:
                sys.stderr.write(line + '\n')
                traceback.print_tb(sys.exc_info()[2])
        os._exit(0)

    ####################
    # METHODS: AT EXIT #
    ####################
    def cleanup(self):
        if self._clean:
            for tfile in self._tempfiles:
                if os.path.isfile(tfile):
                    os.unlink(tfile)
                    self.info('Temporary file {0} removed.'.format(tfile))
            for efile in self.experiment.clean_empty_files():
                self.info('Empty file {0} removed.'.format(efile))
        self._tempfiles = set()

    def shutdown(self):
        self.experiment.end = time.time()
        self.experiment.calculate_duration()

        self._write_to_pipeline()

        info = 'Elapsed time: {0}'.format(self.experiment.duration)
        self._fd.info('[ SUCCESS!! ]: -- {0}'.format(info))
        self._fd.info('[ SUCCESS!! ]: -- Program ended as expected.')

        logging.shutdown()

    ###################
    # PRIVATE METHODS #
    ###################
    def _caller(self, caller):
        if inspect.getmodule(caller) is not None:
            callerID = inspect.getmodule(caller).__name__
        else:
            callerID = 'Terminal'

        if callerID is '__main__':
            callerID = inspect.getmodule(caller).__file__
            callerID = os.path.split(os.path.split(callerID)[0])[-1]
        return callerID.upper()

    def _message_to_array(self, callerID, mssg):
        if isinstance(mssg, basestring):
            mssg = [mssg, ]
        for line in mssg:
            yield self._MSSG.format(callerID, str(line))

    def _write_to_pipeline(self):
        if self.project.is_active:
            data = []
            with open(self.project.pipeline_file, 'r') as line:
                l = line.read().strip()
                if len(l) > 0:
                    data = json.loads(l)
            data.append(self.experiment.to_dict())
            with open(self.project.pipeline_file, 'w') as fd:
                fd.write(json.dumps(data))

    def _configuration(self):
        dfile   = '../config/default.settings'
        ufile   = '../config/user.settings'
        default = os.path.join(os.path.dirname(__file__), dfile)
        default = os.path.normpath(default)
        user    = os.path.join(os.path.dirname(__file__), ufile)
        user    = os.path.normpath(user)
        user    = os.getenv('LIBRARIAN_CONFIG_PY', user)

        parse  = ConfigParser.RawConfigParser(allow_no_value=True)
        parse.readfp(open(default))
        parse.read(user)

        manager_opt = ['stdout',    'verbose',
                       'debug',     'detail',
                       'overwrite', 'unclean']

        for opt in manager_opt:
            func = getattr(self, 'set_' + opt)
            if parse.getboolean('manager', opt):
                self.info('Setting up {0} mode'.format(opt))
                func()
        if parse.get('manager', 'logfile') is not None \
           and parse.get('manager', 'logfile') != '':
            self.set_logfile(parse.get('manager', 'logfile'))

        return [parse.get('project', 'name'),
                parse.get('project', 'config'),
                parse.get('project', 'pipeline')]
