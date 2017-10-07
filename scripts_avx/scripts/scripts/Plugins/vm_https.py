#!../../Python/bin/python
"""."""
import os
import socket
import sys
import subprocess
import shutil
from termcolor import colored
import re
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import logger
lggr = logger.avx_logger('vm_https')
import avx_commons
import signal
from avx_commons import get_username_path
import using_fabric
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class VMHTTPS():
    """The class to initialize common components."""

    def __init__(self):
        """init."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def check_requirements(self):
        """."""
        try:
            self.vm_https = self.conf_data['VM_CONF']['vm_https'][0]
            self.client_trust = self.conf_data['VM_CONF']['enable_client_cert'][0]
            pattern = re.compile(r'^\/.*\.jks$')

            if self.vm_https.upper() == 'TRUE':
                self.keystore_path = self.conf_data['VM_CONF']['key_store_path'][0]
                self.keystore_path = self.keystore_path.replace('{appviewx_dir}', self.path)
                if not(pattern.match(self.keystore_path)):
                    lggr.error('Keystore path not valid in conf file')
                    print('Keystore path not valid in conf file')
                    sys.exit(1)
                folder_path = '/'.join(self.keystore_path.split('/')[:-1])
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                self.keystore_pwd = self.conf_data['VM_CONF']['key_store_pwd'][0]
                self.keymgr_pwd = self.conf_data['VM_CONF']['key_mgr_pwd'][0]
                lggr.debug('Requirements for keystore validated')

            if self.client_trust.upper() == 'TRUE':
                self.truststore_path = self.conf_data['VM_CONF']['trust_store_path'][0]
                self.truststore_path = self.truststore_path.replace('{appviewx_dir}', self.path)
                if not(pattern.match(self.truststore_path)):
                    print('Truststore path not valid in conf file')
                    sys.exit(1)
                folder_path = '/'.join(self.truststore_path.split('/')[:-1])
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                self.truststore_pwd = self.conf_data['VM_CONF']['trust_store_pwd'][0]
                lggr.debug('Requirements for truststore validated')
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def generate_keystore(self):
        """."""
        try:
            cmd = self.path + '/jre/bin/keytool -genkey -alias replserver -keyalg RSA'\
                ' -keystore ' + self.keystore_path + ' -dname "cn=' + self.hostname + ', ou=IT, '\
                ' o=AppViewX, c=US" -storepass ' + self.keystore_pwd + ' -keypass ' + self.keymgr_pwd

            lggr.debug('Command for generating keystore ' + cmd)

            if os.path.isfile(self.keystore_path):
                return

            subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

            if os.path.isfile(self.keystore_path):
                print(colored('keystore generated', 'green'))
                lggr.info('Keystore generated')
            else:
                print(colored('Error in generating server keystore', 'red'))
                print(colored('exiting', 'red'))
                lggr.error('Server keystore not created')
                sys.exit(1)

        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """."""
        try:
            if self.conf_data['VM_CONF']['external_certificates'][0].upper() == 'TRUE':
                lggr.debug('External certifiates provided fo VM HTTPS')
                return True
            self.check_requirements()
            if self.vm_https.upper() == 'TRUE':
                self.generate_keystore()
                lggr.debug('Client keystore created')
            """if self.client_trust.upper() == 'TRUE':
                self.generate_truststore()
                lggr.debug('Client truststore created')"""
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    user_input = sys.argv
    if not len(user_input) == 1:
        print(colored('vm_https.py takes no arguements!', 'red'))
        print(colored('exiting', 'red'))
        sys.exit(1)
    ob = VMHTTPS()
    ob.initialize()
