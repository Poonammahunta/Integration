#!../../Python/bin/python
"""Script to initialize gateway."""
import os
import sys
from termcolor import colored
import socket
import subprocess
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
from avx_commons import execute_on_particular_ip
from avx_commons import run_local_cmd
from initialize_common import InitializeCommon
import logger
import set_path
import jssecacerts
avx_path = set_path.AVXComponentPathSetting()
lggr = logger.avx_logger('initialize_gateway')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class InitializeGateway():
    """Class to initialize gateway."""

    def __init__(self, ip=False):
        """."""
        try:
            from config_parser import config_parser
            self.ip = ip
            self.path =avx_path.appviewx_path
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    @staticmethod
    def find_and_replace(filename, partial, replacement):
        """."""
        try:
            with open(filename) as open_file:
                file_content = open_file.readlines()
            for line in file_content:
                if partial in line:
                    file_content[file_content.index(line)] = replacement + '\n'
                    break
            with open(filename, 'w+') as open_file:
                open_file.write(''.join(file_content))
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def gateway_https(self):
        if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
            gateway_myserver_cert = self.conf_data['SSL']['ssl_gateway_key'][0].replace('{appviewx_dir}', self.path)

            if not os.path.exists(
                    gateway_myserver_cert):
                print(
                    gateway_myserver_cert +
                    ' missing!!')
                print('exiting!!')
                sys.exit(1)
            else:
                gateway_password = self.conf_data[
                    'SSL']['gateway_key_password'][0]
                cmd = 'openssl pkcs12 -nocerts -in "' + gateway_myserver_cert + '" -out ' + self.path + '/server.key -password pass:' + \
                    gateway_password + ' -passin pass:' + gateway_password + ' -passout pass:' + gateway_password + ' > /dev/null 2>&1'
                subprocess.run(cmd , shell=True)
                cmd = 'openssl rsa -in ' + self.path + '/server.key -out "' + \
                    self.path + '/server.key" -passin pass:' + gateway_password + ' > /dev/null 2>&1'
                subprocess.run(cmd, shell=True)
                cmd = "openssl pkcs12 -in " + gateway_myserver_cert + " -clcerts -nokeys -password pass:" + \
                    gateway_password + " -out " + self.path + "/server.crt" + ' > /dev/null 2>&1'
                subprocess.run(cmd + ' 2>&1 >/dev/null', shell=True)

    def initialize(self):
        """."""
        try:
            self.gateway_https()
            if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower()== 'true':
                jssecacerts_obj = jssecacerts.Jssecacerts_Creator(self.conf_data)
                jssecacerts_obj.initialize()
            try:
                gateway_key = open(current_file_path + '/../../avxgw/Gateway_key.txt').read().strip()
                lggr.debug('gateway_key = ' + gateway_key)
            except IOError:
                print(colored('Gateway_key.txt not found!', 'red'))
                lggr.error('Gateway_key.txt file not found in avxgw/ directory')
                return False

            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                username = self.conf_data['ENVIRONMENT']['username'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                cmd = 'ssh -oStrictHostKeyChecking=no ' + username + '@' + self.ip + \
                    ' sed -i "s/APPVIEWX_GATEWAY_KEY.*/APPVIEWX_GATEWAY_KEY=%s/g" %s/conf/appviewx.conf' % (gateway_key, path)
                execute_on_particular_ip(self.conf_data, self.ip, cmd)
                return
            ips = self.conf_data['GATEWAY']['ips']
            node_details = []
            for username, ip in zip(
                    self.conf_data['ENVIRONMENT']['username'],
                    self.conf_data['ENVIRONMENT']['ips']):
                if ip in ips:
                    node_details.append(username + '@' + ip)
            paths = self.conf_data['ENVIRONMENT']['path']
            for node, path in zip(node_details, paths):
                conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(node.split(':')[0].split('@')[1])]
                conn_port = str(conn_port)
                if self.hostname in node:
                    self.conf_file = current_file_path + '/../../conf/appviewx.conf'
                    str_to_replace = 'APPVIEWX_GATEWAY_KEY'
                    str_to_replace_with = 'APPVIEWX_GATEWAY_KEY=' + gateway_key
                    self.find_and_replace(self.conf_file, str_to_replace, str_to_replace_with)
                    str_to_replace = 'appviewx_gateway_key'
                    str_to_replace_with = 'appviewx_gateway_key=' + gateway_key
                    self.find_and_replace(self.conf_file, str_to_replace, str_to_replace_with)
                    lggr.info('Gateway key updated in conf file')
                else:
                    cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + node + \
                        ' sed -i "s/APPVIEWX_GATEWAY_KEY.*/APPVIEWX_GATEWAY_KEY=%s/g" %s/conf/appviewx.conf' % (gateway_key, path)
                    run_local_cmd(cmd)
                    cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + node + \
                        ' sed -i "s/appviewx_gateway_key.*/appviewx_gateway_key=%s/g" %s/conf/appviewx.conf' % (gateway_key, path)
                    run_local_cmd(cmd)
                    lggr.debug('Gateway key updated in conf file on ' + ip)

            obj = InitializeCommon()
            obj.update_property_file()
            lggr.info('Property file updated')
            return True
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
        obj = InitializeGateway()
        flag = obj.initialize()
        if flag:
            print(colored('Gateway Initialized', 'green'))
            lggr.info('Gateway Initialized')
        else:
            lggr.error('Some error in initializing gateway')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)

