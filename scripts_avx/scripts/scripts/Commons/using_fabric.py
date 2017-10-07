'''Base class for ssh communication
Example:
 command=AppviewxShell(hostname=['192.168.50.99','192.168.42.160'],user='appviewx')
 print command.run(cmd='ls')'''

from fabric.api import *
import fabric
import socket
import warnings
warnings.filterwarnings("ignore")
import getpass
import os
from config_parser import config_parser
conf_data = config_parser(os.path.dirname(os.path.realpath(__file__)) + '/../../conf/appviewx.conf')
local_hostname = getpass.getuser()
hostname = socket.gethostbyname(socket.gethostname())
import logger
lggr = logger.avx_logger('FABFILE')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

def print_progress(self, transferred, tobetransferred):
    '''
       Callback function to calculate the percentage progressed
    '''
    progress = (transferred / float(tobetransferred)) * 100
    print(progress)


class AppviewxShell(object):

    ''' Custom class with fabric to execute all the remote commands for AppViewX scripts.'''

    def __init__(self, hostname=None, cmd=None, user=None, pty=True,port=22, parallel=False):
        '''Host and user details are stored for fabric execution
        @param hostname type: List
        @param hostname: List of ip address

        '''
        if hostname:
            env.hosts = hostname
        if user:
            env.user = user
        else:
            try:
                if len(hostname) == 1:
                    env.user = conf_data['ENVIRONMENT']['username'][self.conf_data['ENVIRONMENT']['ips'].index(hostname)]
                else:
                    env.user = conf_data['ENVIRONMENT']['username'][0]
            except:
                env.user = conf_data['ENVIRONMENT']['username'][0]

        self.pty = pty
        try:
            env.port = conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(hostname[0])]
        except Exception:
            env.port = 22
        # fabric output would be suppressed
        fabric.state.output['running'] = False
        fabric.state.output['output'] = False
        self.cmd = cmd
        self.parallel = parallel
        env.parallel = parallel

    def _exec_remote_cmd(self):
        ''' Private function to execute the command with the default settings. Not to be used by the external system'''
        try:
            with hide('warnings'), settings(warn_only=True, parallel=self.parallel, capture=True):
                lggr.debug('Fabric env details : hosts: %s , user : %s, port : %s' %(env.hosts,env.user,env.port))
                lggr.debug('Executing commands [%s] %s@%s' % (self.cmd,env.user,env.hosts[0]))
                lggr.info('Executing commands [%s] %s@%s' % (self.cmd,env.user,env.hosts[0]))
                if env.hosts[0] == hostname and env.user == local_hostname:
                    lggr.debug('Executing as local environment')
                    result = local(self.cmd, capture=True)
                else:
                    lggr.debug('Executing in remote environment')
                    if self.pty:
                        result = run(self.cmd)
                    else:
                        result = run(self.cmd, pty=self.pty)
                return result, result.succeeded
        except Exception:
            raise Exception

    def run(self, cmd, user='appviewx'):
        ''' This function to be called with an object to execute the command.
                  @param cmd type: String - command to be executed on the remote shell
                  @param cmd
                  @param parallel:Type boolean default serial execution is set and can be changed to True for parallel execution
                 Example:
                  >command=AppviewxShell(hostname=['192.168.50.99','192.168.42.160'],user='appviewx')
                  >print command.run(cmd='ls')
        '''
        try:
            self.cmd = cmd
            self.result = execute(self._exec_remote_cmd)
            lggr.debug('Result of the executed commands : %s - %s ' % (self.result.keys(), self.result.values()))
            return self.result.keys(), self.result.values()
        except Exception:
            raise Exception

    def _file_send(self):
        try:
            result = put(
                self.localpath,
                self.remotepath,
                mirror_local_mode=True)
            if result.succeeded:
                return 'Success'
            else:
                return 'Failed'
        except Exception:
            return 'Error'

    def file_send(self, localpath, remotepath):
        try:
            self.localpath = localpath
            self.remotepath = remotepath
            try:
                self.result = execute(self._file_send)
            except:
                print('Some problem in sending the file: ' + localpath + ' to ' + env.hosts[0])
            result = []
            for k, v in self.result.items():
                result.append(k + ':' + v + '\n')
            return ''.join(result)

        except Exception as e:
            print(e)
