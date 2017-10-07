#!../../Python/bin/python
"""."""
import os
import socket
import sys
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import using_fabric
from avx_commons import return_status_message_fabric
from avx_commons import get_username_path
from avx_commons import execute_on_particular_ip
from avx_commons import run_local_cmd
import logger
lggr = logger.avx_logger('initialize mongodb')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class InitializeMongoDB():
    """."""

    def __init__(self, ip=False):
        """."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.ip = ip
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """."""
        try:
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                db_setup = path + '/Python/bin/python ' + path + '/scripts/Mongodb/db_setup_python.py >/dev/null 2>&1'
                execute_on_particular_ip(self.conf_data, self.ip, db_setup)
                return

            for ip in self.conf_data['MONGODB']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                db_setup = path + '/Python/bin/python ' + path + '/scripts/Mongodb/db_setup_python.py >/dev/null 2>&1'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(db_setup)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('Error in initializing mongodb on: ' + ip)
                else:
                    lggr.debug('Mongodb initialized on: ' + ip)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
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
        obj = InitializeMongoDB(ip)
        obj.initialize()
        print(colored('MongoDB Initialized', 'green'))
        lggr.info('MongoDB Initialized successfully')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
