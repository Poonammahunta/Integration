"""."""
import os
import socket
import sys
from termcolor import colored
import logger
current_file_path = os.path.dirname(os.path.realpath(__file__))
from avx_commons import run_local_cmd
lggr = logger.avx_logger('push_lb')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class PushLB():
    """."""

    def __init__(self, path, db_ip, db_port):
        """."""
        try:
            from avx_commons import get_db_credentials
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.db_username, self.db_password, self.db_name = get_db_credentials()
            self.db_ip = db_ip
            self.db_port = db_port
            self.path = path
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    @staticmethod
    def generate_load_balancer():
        """."""
        try:
            cmd_load_balancer = current_file_path + '/../../Python/bin/python '\
                + current_file_path + '/load_balancer.py'

            run_local_cmd(cmd_load_balancer)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def push_load_balancer(self):
        """."""
        try:
            check = os.path.isfile(current_file_path + 'gateway_loadbalancer.js')
            if check == 'False':
                print('no load_balancer.js file found')
                lggr.error('gateway_loadbalancer.js not found!')
                print('exiting!')
                sys.exit(1)
            mongo = self.path + '/db/mongodb/bin/mongo'
            lb_cmd = mongo + ' ' + self.db_ip + ':' + self.db_port + '/gateway -u ' \
                + self.db_username + ' -p ' + self.db_password + ' --authenticationDatabase ' \
                + self.db_name + ' --quiet ' + self.path + '/scripts/Commons/gateway_loalbalancer.js'
            dbrm_cmd = mongo + ' ' + self.db_ip + ':' + self.db_port + '/gateway -u ' \
                + self.db_username + ' -p ' + self.db_password + ' --authenticationDatabase ' \
                + self.db_name + ' --quiet ' + self.path + '/scripts/Commons/dbremove.js'
            system_component_cmd = mongo + ' ' + self.db_ip + ':' + self.db_port + '/appviewx -u ' \
                + self.db_username + ' -p ' + self.db_password + ' --authenticationDatabase ' \
                + self.db_name + ' --quiet ' + self.path + '/scripts/Commons/system_components.js'
            run_local_cmd(dbrm_cmd)
            run_local_cmd(lb_cmd)
            print(lb_cmd)
            run_local_cmd(system_component_cmd)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """."""
        try:
            self.generate_load_balancer()
            self.push_load_balancer()
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    try:
        lggr.info('Inside push_lb.py')
        user_input = sys.argv
        if len(user_input) != 4:
            print('The file takes three inputs')
            print('path, db_ip, db_port')
            print('exiting')
            sys.exit(1)
        path = user_input[1]
        db_ip = user_input[2]
        db_port = user_input[3]
        lggr.debug('Load Balancer initialization started')
        ob = PushLB(path, db_ip, db_port)
        ob.initialize()
        lggr.debug('Load balancer intialization completed')
        print(colored('Load balancer pushed', 'green'))
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
