"""."""
import os
import sys
import subprocess
import socket
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_path + '/../Commons')
from termcolor import colored
import set_path
avx_path = set_path.AVXComponentPathSetting()
import logger
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('self_signed_certs')

import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class SelfSignedCertificates():
    """Class to Create self signed certificates."""

    def __init__(self):
        """Init function for class SelfSignedCertificates."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            self.web_pass = self.conf_data['SSL']['web_key_password'][0]
            self.gateway_pass = self.conf_data['SSL']['gateway_key_password'][0]
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def remove_existing(self):
        """."""
        files_to_remove = [self.path + 'server.key',
                           self.path + 'server.crt',
                           self.path + 'server.csr']
        for file in files_to_remove:
            try:
                os.remove(file)
            except:
                pass

    def create(self):
        """."""
        try:
            cmd = 'openssl genrsa -out server.key 2048'
            subprocess.run(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            cmd = 'openssl req -new -key server.key -passin pass:appviewx@123 -out server.csr -subj "/CN=' + \
                str(self.hostname) + '"'
            subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            cmd = 'openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt'
            subprocess.run(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            cmd = 'openssl pkcs12 -export -clcerts -in server.crt -inkey server.key -password pass:' + self.web_pass + ' -out ' + self.conf_data['SSL']['ssl_web_key'][0].replace('{appviewx_dir}',avx_path.appviewx_path)
            subprocess.run(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            cmd = 'openssl pkcs12 -export -clcerts -in server.crt -inkey server.key -password pass:' + self.gateway_pass + ' -out ' + self.conf_data['SSL']['ssl_gateway_key'][0].replace('{appviewx_dir}',avx_path.appviewx_path)
            subprocess.run(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            lggr.debug('Self signed certificates created')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def get_key_crt_from_cert(self):
        """Function to get ey and crt from certificate."""
        self.web_key = self.conf_data['SSL']['ssl_web_key'][
            0].replace('{appviewx_dir}', self.path)
        self.gateway_key = self.conf_data['SSL']['ssl_gateway_key'][
            0].replace('{appviewx_dir}', self.path)
        cmd_to_get_web_key = 'openssl pkcs12 -nocerts -in "' + self.web_key +\
            '"  -password pass:' + self.web_pass +\
            ' -passin pass:appviewx@123 -passout pass:appviewx@123'
        cmd_to_get_gateway_key = 'openssl pkcs12 -nocerts -in "' +\
            self.gateway_key +\
            '"  -password pass:' + self.gateway_pass +\
            ' -passin pass:appviewx@123 -passout pass:appviewx@123'

        web_key_file_content = subprocess.run(cmd_to_get_web_key,
                                              shell=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE
                                              ).stdout.decode()
        gateway_key_file_content = subprocess.run(cmd_to_get_gateway_key,
                                                  shell=True,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE
                                                  ).stdout.decode()
        with open(self.path + '/web.key', 'w+') as webkey:
            webkey.write(web_key_file_content)
        with open(self.path + '/gateway.key', 'w+') as webkey:
            webkey.write(gateway_key_file_content)
        for file in [self.path + '/web.key', self.path + '/gateway.key']:
            cmd = 'openssl rsa -in ' + file + ' -out "' + file +\
                '" -passin pass:appviewx@123'
            alias = '.'.join(file.split('/')[-1].split('.')[:-1])
            if 'web' in file.lower():
                passwd = self.web_pass
                c_file = self.web_key
            else:
                passwd = self.gateway_pass
                c_file = self.gateway_key
            final_cmd = 'openssl pkcs12 -in ' + c_file + \
                ' -clcerts -nokeys -password pass:' + passwd + ' -out ' +\
                self.path + '/' + alias + '.crt'
            subprocess.run(cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            subprocess.run(final_cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        key_content = ''
        crt_content = ''
        with open(self.path + '/web.key') as webkey:
            key_content += webkey.read() + '\n\n\n'
        with open(self.path + '/gateway.key') as gatekey:
            key_content += gatekey.read() + '\n\n\n'
        with open(self.path + '/server.key', 'w+') as server_key:
            server_key.write(key_content)

        with open(self.path + '/web.crt') as webcrt:
            crt_content += webcrt.read() + '\n\n\n'
        with open(self.path + '/gateway.crt') as gatecrt:
            crt_content += gatecrt.read() + '\n\n\n'
        with open(self.path + '/server.crt', 'w+') as server_crt:
            server_crt.write(crt_content)

        for file in [self.path + '/web.key',
                     self.path + '/gateway.key',
                     self.path + '/web.crt',
                     self.path + '/gateway.crt']:
            try:
                os.remove(file)
            except:
                lggr.debug('Unable to remove file: ' + file)

    def initialize(self):
        """."""
        try:
            pwd = os.getcwd()
            os.chdir(self.path)
            self.remove_existing()
            self.create()
            os.chdir(pwd)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)


if __name__ == '__main__':
    try:
        user_input = sys.argv
        ob = SelfSignedCertificates()
        if len(user_input) == 1:
            ob.initialize()
        else:
            ob.get_key_crt_from_cert()
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
