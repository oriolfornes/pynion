"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import atexit
import collections
import datetime
import inspect
import json
import logging
import os
import pwd
import re
import socket
import subprocess
import sys
import time
import warnings

from ..decorators import singleton
from .process     import Process


@singleton
class Manager(object):

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

        # Experiment Conditions:
        self.experiment_name   = None
        self.experiment_user   = pwd.getpwuid(os.getuid())[0]
        self.experiment_host   = socket.gethostname()
        self.experiment_wdir   = os.getcwd()
        self.experiment_date   = None
        self.experiment_files  = set()
        self.experiment_config = None
        self.experiment_pipe   = None
        self.experiment_start  = time.time()

        self.retrieve_experiment()

        # Create a logger.
        # Null handler is added so that if no handler is active
        # warnings and errors will not display a 'handler not found' message
        self._fd = logging.getLogger(__name__)
        self._fd.setLevel(logging.DEBUG)
        self._fd.addHandler(logging.NullHandler())

        # Register function to execute at exit
        atexit.register(self.shutdown)
        atexit.register(self.cleanup)

    ####################
    # METHODS: SETTERS #
    ####################
    def set_verbose(self):
        self.set_stdout()
        self._verbose = True

    def set_debug(self):
        self.set_verbose()
        self._debug  = True

    def set_detail(self):
        self._detail = True
        self.set_clean()
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

    def set_experiment_date(self, year, month, day):
        self.experiment_date = datetime.date(year, month, day)

    def set_experiment_configuration_file(self, filename):
        if filename is None:
            return
        self._experiment_config_file(filename)

        self.info(['Linking experiment configuration file:',
                   '{0}.'.format(self.experiment_config)])
        if not os.path.isfile(self.experiment_config):
            fd = open(self.experiment_config, 'w')
            fd.close()

    ###########
    # METHODS #
    ###########
    def experiment_summary(self):
        today = datetime.date.today()
        data  = ['# Experiment:',
                 '# By: {0}'.format(self.experiment_user),
                 '# At: {0}'.format(self.experiment_host),
                 '# On: {0}'.format(today.isoformat())]
        if self.experiment_date is not None:
            expday = self.experiment_date
            data.append('# TimeStamp: {0}'.format(expday.isoformat()))
        self.info(data)

    def add_tempfile(self, tempfile):
        self._tempfiles.add(tempfile)

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
        os._exit(0)

    ###############################
    # METHODS: EXPERIMENT SUMMARY #
    ###############################
    def init_experiment(self):
        self._experiment_pipeline_file()

        data = collections.OrderedDict()
        data['name']   = self.experiment_name
        data['user']   = self.experiment_user
        data['host']   = self.experiment_host
        data['wdir']   = self.experiment_wdir
        data['date']   = self.experiment_date.isoformat()
        data['config'] = self.experiment_config
        data['ppline'] = self.experiment_pipe

        data = json.dumps(data, indent=4, separators=(',', ':'))

        self.info(['Creating experiment properties file:',
                   '{0}.'.format(self._experiment_log_file())])
        fd = open(self._experiment_log_file(), 'w')
        fd.write(data)
        fd.close()
        self.info(['Creating experiment pipeline file:',
                   '{0}.'.format(self.experiment_pipe)])
        if not os.path.isfile(self.experiment_pipe):
            self.write_to_pipeline()

    def retrieve_experiment(self):
        if not os.path.isfile(self._experiment_log_file()):
            return
        fd   = open(self._experiment_log_file())
        data = json.loads(''.join([x.strip() for x in fd.readlines()]))
        fd.close()
        self.experiment_name   = data['name']
        self.experiment_wdir   = data['wdir']
        data['date'] = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
        self.experiment_date   = data['date']
        self.experiment_config = data['config']
        self.experiment_pipe   = data['ppline']

        self.write_to_pipeline()

    def write_to_pipeline(self):
        process = self._get_process()
        fd = open(self.experiment_pipe, 'a')
        fd.write('#user: {0}\n'.format(process.user))
        for efile, eaction in self.experiment_files:
            if eaction.startswith('r'):
                fd.write('#read file: {0}\n'.format(efile))
            if eaction.startswith('w'):
                fd.write('#written file: {0}\n'.format(efile))
        fd.write('{0}\n'.format(process.cmd))
        fd.close()

    ####################
    # METHODS: AT EXIT #
    ####################
    def cleanup(self):
        if self._clean:
            for tfile in self._tempfiles:
                if os.path.isfile(tfile):
                    os.unlink(tfile)
                    self.info('Temporary file {0} removed'.format(tfile))
            for efile, eaction in self.experiment_files:
                if os.path.isfile(efile) and os.path.getsize(efile) == 0:
                    if eaction.startswith('w'):
                        os.unlink(efile)
                        self.info('Empty file {0} removed'.format(efile))
        self._tempfiles = set()

    def shutdown(self):
        experiment_end    = time.time()
        experiment_length = experiment_end - self.experiment_start
        experiment_length = str(datetime.timedelta(seconds=experiment_length))
        experiment_length = 'Elapsed time: {0}'.format(experiment_length)
        self._fd.info('[ SUCCESS!! ]: -- {0}'.format(experiment_length))
        self._fd.info('[ SUCCESS!! ]: -- Program ended as expected.')
        logging.shutdown()

    ###################
    # PRIVATE METHODS #
    ###################
    def _experiment_log_file(self):
        return os.path.join(self.experiment_wdir, '_info.exp-properties')

    def _experiment_config_file(self, filename):
        if not filename.endswith('.exp-config'):
            filename += '.exp-config'
        self.experiment_config = filename

    def _experiment_pipeline_file(self):
        self.experiment_pipe = '_info.exp-pipeline'

    def _caller(self, caller):
        callerID = inspect.getmodule(caller).__name__
        if callerID is '__main__':
            callerID = inspect.getmodule(caller).__file__
            callerID = os.path.split(os.path.split(callerID)[0])[-1]
        return callerID.upper()

    def _message_to_array(self, callerID, mssg):
        if isinstance(mssg, basestring):
            mssg = [mssg, ]
        for line in mssg:
            yield self._MSSG.format(callerID, str(line))

    def _get_process(self):
        sub_proc = subprocess.Popen(['ps', 'aux'],
                                    shell=False, stdout=subprocess.PIPE)
        #Discard the first line (ps aux header)
        sub_proc.stdout.readline()
        pid = int(os.getpid())
        for line in sub_proc.stdout:
            #The separator for splitting is 'variable number of spaces'
            proc_info = re.split(" *", line.strip())
            p = Process(proc_info)
            if p.pid == pid:
                return p
