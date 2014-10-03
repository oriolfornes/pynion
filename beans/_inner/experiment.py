"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import collections
import datetime
import os
import platform
import pwd
import re
import socket
import subprocess
import sys
import time

from .. import JSONer
from .  import Process


class Experiment(JSONer):
    _PIPELINE_FILE = '_pipeline-project.json'

    def __init__(self):
        self.pyversion = platform.python_version()
        self.command   = sys.argv
        self.user      = pwd.getpwuid(os.getuid())[0]
        self.host      = socket.gethostname()
        self.system    = (platform.system(), platform.release())
        self.files     = set()
        self.start     = time.time()
        self.end       = None
        self.length    = None

        self.process   = None
        try:
            self.process = self._get_process()
            print self.process
        except:
            from .. import Manager
            m = Manager()
            m.warning(['Bash command could not be imported.',
                       'System needs to be UNIX based'])

    ####################
    # METHODS: AT EXIT #
    ####################
    def calculate_length(self):
        self.length = self.end - self.start
        self.length = str(datetime.timedelta(seconds=self.length))

    def clean_empty_files(self):
        from ..manager import Manager
        m = Manager()

        for efile, eaction in self.files:
            if os.path.isfile(efile) and os.path.getsize(efile) == 0:
                if eaction.startswith('w'):
                    os.unlink(efile)
                    m.info('Empty file {0} removed'.format(efile))

    ###################
    # METHODS: JSONer #
    ###################
    def _toDICT(self):
        json = collections.OrderedDict()
        json['command']   = self.command
        if self.process is not None:
            json['bash']  = self.process.cmd
        json['pyversion'] = self.pyversion
        json['user']      = self.user
        json['host']      = self.host
        json['system']    = list(self.system)
        json['duration']  = self.length
        json['inputs']    = []
        json['outputs']   = []
        for efile, eaction in self.files:
            if eaction.startswith('r'):
                json['inputs'].append(efile)
            elif eaction.startswith('w'):
                json['outputs'].append(efile)
        return json

    ###################
    # METHODS: JSONer #
    ###################
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
