#!../../Python/bin/python
"""."""
import os
import sys
import socket
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import using_fabric
from avx_commons import return_status_message_fabric
from avx_commons import get_username_path
from avx_commons import execute_on_particular_ip
from avx_commons import run_local_cmd


import logger
lggr = logger.avx_logger('initialize _web')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class InitializeWeb():
    """."""

    def __init__(self, ip=False):
        """."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.ip = ip
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def web_local_data(self):
        """."""
        try:
            web_https = self.conf_data['WEB']['appviewx_web_https'][0]
            web_multinode = self.conf_data['ENVIRONMENT']['multinode'][0]
            if web_https.upper() == 'TRUE':
                local_web_cmd = self.path + '/Python/bin/python ' + \
                    self.path + '/scripts/Web/local_web_https.py '
            else:
                local_web_cmd = self.path + '/Python/bin/python ' + \
                    self.path + '/scripts/Web/local_web_http.py '
            return web_https, web_multinode, local_web_cmd
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)

    def initialize(self):
        """."""
        try:
            https = self.conf_data['WEB']['appviewx_web_https'][0]
            if https.upper() == 'FALSE':
                http_tag = 'http'
                lggr.debug('HTTP Web')
            else:
                http_tag = 'https'
                lggr.debug('HTTPS Web')

            file_to_call = 'local_web_' + http_tag + '.py'
            local_web_cmd = self.path + '/Python/bin/python ' + \
                self.path + '/scripts/Web/' + file_to_call

            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                local_web_cmd = path + '/Python/bin/python ' + path + '/scripts/Web/' + file_to_call
                execute_on_particular_ip(self.conf_data, self.ip, local_web_cmd)
                return

            for ip in self.conf_data['WEB']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                local_web_cmd = path + '/Python/bin/python ' + \
                    path + '/scripts/Web/' + file_to_call
                lggr.debug('command: ' + local_web_cmd)
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(local_web_cmd)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('Error in initializing web on: ' + ip)
                else:
                    lggr.debug('Web initialized on: ' + ip)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    try:
        try:
            user_input = sys.argv
            ip = user_input[1]
        except:
            ip = False
        obj = InitializeWeb(ip)
        obj.initialize()
        print(colored('Web initialized', 'green'))
        lggr.info('Web Initialized')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
