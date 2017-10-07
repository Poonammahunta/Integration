#!../../Python/bin/python
"""Script to initialize logstash."""
import os
import sys
from termcolor import colored
import socket
import subprocess
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
from avx_commons import execute_on_particular_ip,get_username_path
from avx_commons import run_local_cmd
import logger
import set_path
avx_path = set_path.AVXComponentPathSetting()
lggr = logger.avx_logger('initialize_logstash')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import using_fabric

class Initializelogstash(object):
    """Class to initialize logstash."""

    def __init__(self, ip=False):
        """."""
        try:
            from config_parser import config_parser
            self.ip = ip
            self.path =avx_path.appviewx_path
            self.conf_file = self.path + '/conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)


    def initialize(self):
      
        if self.ip:
              path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
              db_setup = path + '/Python/bin/python ' + path + '/scripts/Logstash/logstash_configuration.py'
              execute_on_particular_ip(self.conf_data, self.ip, db_setup)
        else:
              for ip in self.conf_data['LOGSTASH']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                logstash_conf_cmd = path + '/Python/bin/python ' + path + '/scripts/Logstash/logstash_configuration.py'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(logstash_conf_cmd)
                status, res = avx_commons.return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('Error in initializing Logstash on: ' + ip)
                else:
                    lggr.debug('Logstash initialized on: ' + ip)
    
if __name__ == '__main__':
    try:
        try:
            user_input = sys.argv
            ip = user_input[1]
        except:
            ip = False
        obj = Initializelogstash()
        flag = obj.initialize()
        print(colored('logstash Initialized', 'green'))
        lggr.info('logstash Initialized')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)

