#!../../Python/bin/python
"""."""
import os
import socket
import sys
import subprocess
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import using_fabric
from avx_commons import return_status_message_fabric
from avx_commons import get_username_path
from avx_commons import execute_on_particular_ip
import logger
lggr = logger.avx_logger('Initialize Plugins')
import avx_commons
import signal
import fabric
import shutil
from fabric.api import *
fabric.state.output['warnings'] = False
fabric.state.output['output'] = False
fabric.state.output['running'] = False
fabric.state.output['everything'] = False
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class InitializePlugins():
    """Class to initialize plugins."""

    def __init__(self, ip=False):
        """Init function for initializing lugins."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.ip = ip
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            self.truststore_path = self.conf_data['VM_CONF']['trust_store_path'][0]
            self.truststore_path = self.truststore_path.replace('{appviewx_dir}', self.path)
            self.truststore_pwd = self.conf_data['VM_CONF']['trust_store_pwd'][0]
            self.client_trust = self.conf_data['VM_CONF']['enable_client_cert'][0]
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def check_if_exists(self):
        """."""
        from avx_commons import return_status_message_fabric
        to_exit = True
        for ip in self.conf_data['ENVIRONMENT']['ips']:
            user, path = get_username_path(self.conf_data, ip)
            file_name = self.truststore_path.split('/')[-1]
            cmd = 'ls ' + '/'.join(self.truststore_path.split('/')[:-1])
            fab_ob = using_fabric.AppviewxShell([ip], user=user)
            l = fab_ob.run(cmd)
            stat, res = return_status_message_fabric(l)
            if file_name not in res:
                to_exit = False

        return to_exit

    def generate_truststore(self):
        """."""
        try:
            to_exit = False
            if os.path.exists(self.path + '/client.key') and os.path.exists(self.path + '/client.crt') and os.path.exists(self.path + '/client-ca.key'):
                to_exit = True
            to_exit = to_exit * self.check_if_exists()
            if to_exit:
                return
            pwd = os.getcwd()
            os.chdir('/'.join(self.truststore_path.split('/')[:-1]))
            client_key = []
            client_crt = []

            try:
                os.remove('client.key')
                os.remove('client.csr')
                os.remove('client.crt')
            except:
                lggr.debug('client files unable to delete')

            for host in self.conf_data['ENVIRONMENT']['ips']:
                cmd_list = ['openssl genrsa -out client.key 2048',
                            'openssl req -new -key client.key -passin pass:appviewx@123 -out client.csr -subj "/CN=' + str(host) + '"',
                            'openssl x509 -req -days 365 -in client.csr -signkey client.key -out client.crt']

                for cmd in cmd_list:
                    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                key_con = open('client.key').read()
                crt_con = open('client.crt').read()
                client_key.append('\n' + key_con)
                client_crt.append('\n' + crt_con)

            with open('client.key', 'w+') as keyfile:
                keyfile.writelines(client_key)
            with open('client.crt', 'w+') as crtfile:
                crtfile.writelines(client_crt)

            cer_file = 'client.crt'
            if not os.path.isfile(cer_file):
                print('Certificate not formed!')
                sys.exit(1)

            if os.path.isfile(self.truststore_path):
                os.remove(self.truststore_path)

            cmd_for_truststore = self.path + '/jre/bin/keytool -import -trustcacerts '\
                '-alias replserver -file ' + cer_file + ' -keystore ' + \
                self.truststore_path + ' -storepass ' + self.truststore_pwd + ' -noprompt'
            subprocess.run(
                cmd_for_truststore,
                shell=True,
                stderr=subprocess.PIPE)
            if os.path.isfile(self.truststore_path):
                lggr.info('Truststore generated for client ssl')
            else:
                print(colored('Error in generating client truststore', 'red'))
                print(colored('exiting', 'red'))
                lggr.error('Client Truststore not created')
                sys.exit(1)

            os.chdir(pwd)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def copy_files_to_other_nodes(self):
        """Function to copy key, crt and truststore to all nodes."""
        from using_fabric import AppviewxShell
        nodes_to_send = self.conf_data['ENVIRONMENT']['ips'] * 1
        for node in nodes_to_send:
            user, path = get_username_path(self.conf_data, node)
            f_ob = AppviewxShell([node], user)
            key_origin = '/'.join(self.truststore_path.split('/')[:-1]) + '/client.key'
            crt_origin = '/'.join(self.truststore_path.split('/')[:-1]) + '/client.crt'

            key_dest = path + '/client.key'
            key_ca_dest = path + '/client-ca.key'
            crt_dest = path + '/client.crt'

            f_ob.file_send(key_origin, key_dest)
            f_ob.file_send(key_origin, key_ca_dest)
            f_ob.file_send(crt_origin, crt_dest)

        nodes_to_send.remove(self.hostname)
        for node in nodes_to_send:
            user, path = get_username_path(self.conf_data, node)
            f_ob = AppviewxShell([node], user)
            temp_path = self.conf_data['VM_CONF']['trust_store_path'][0]
            l_path = self.truststore_path
            r_path = temp_path.replace('{appviewx_dir}', path)
            f_ob.file_send(l_path, r_path)

    def initialize(self):
        """."""
        try:
            path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            vm_https = path + '/Python/bin/python ' + path + '/scripts/Plugins/vm_https.py >/dev/null 2>&1'
            plugin_log = path + '/Python/bin/python ' + path + '/scripts/Plugins/plugin_log4j.py >/dev/null 2>&1'
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                vm_https = path + '/Python/bin/python ' + path + '/scripts/Plugins/vm_https.py >/dev/null 2>&1'
                plugin_log = path + '/Python/bin/python ' + path + '/scripts/Plugins/plugin_log4j.py >/dev/null 2>&1'
                execute_on_particular_ip(self.conf_data, self.ip, vm_https)
                execute_on_particular_ip(self.conf_data, self.ip, plugin_log)
                return
            for user, ip, path in zip(self.conf_data['ENVIRONMENT']['username'],
                                      self.conf_data['ENVIRONMENT']['ips'],
                                      self.conf_data['ENVIRONMENT']['path']):
                vm_https = path + '/Python/bin/python ' + path + '/scripts/Plugins/vm_https.py >/dev/null 2>&1'
                plugin_log = path + '/Python/bin/python ' + path + '/scripts/Plugins/plugin_log4j.py >/dev/null 2>&1'
                cmds = [vm_https, plugin_log]
                command = using_fabric.AppviewxShell([ip], user=user)
                for cmd in cmds:
                    f_obj = command.run(cmd)
                    status, res = return_status_message_fabric(f_obj)
                    if not status:
                        lggr.error('Error in initializing plugins on: ' + ip)
                    else:
                        lggr.debug('Plugins initialized on: ' + ip)
            """if self.conf_data['VM_CONF']['enable_client_cert'][0].upper() == 'TRUE':
                CopyCrtKey.initialize(CopyCrtKey())"""
            if self.client_trust.upper() == 'TRUE':
                self.generate_truststore()
                lggr.debug('Client truststore created')
                self.copy_files_to_other_nodes()
            self.merge_into_one_truststore()
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def merge_into_one_truststore(self):
        """."""
        if self.client_trust.upper() == 'FALSE':
            return
        temp_path = os.path.abspath(self.path + '/scripts/temp')
        if not os.path.exists(temp_path):
            os.makedirs(self.path + '/scripts/temp')
        from jssecacerts import put_file
        from jssecacerts import put_file_remote
        for ip in self.conf_data['ENVIRONMENT']['ips']:
            user, path = get_username_path(self.conf_data, ip)
            port = self.conf_data['ENVIRONMENT'][
                'ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(ip)]
            files = ['server.crt', 'client.crt']
            for file in files:
                if file == 'server.crt' and ip not in self.conf_data[
                        'GATEWAY']['ips']:
                    continue
                execute(put_file,
                        localpath=os.path.abspath(
                            temp_path + '/' + ip + '_' + file),
                        remotepath=os.path.abspath(path + '/' + file),
                        hosts=user + '@' + ip + ':' + port)
        cwd = os.getcwd()
        os.chdir(temp_path)
        for file in os.listdir(temp_path):
            alias = ''
            if 'client' in file:
                alias += 'client-'
            else:
                alias = 'server-'
            alias += file.split('_')[0]
            cmd = self.path + '/jre/bin/keytool -noprompt -import -alias ' +\
                alias + ' -storepass changeit -file ' + file +\
                ' -keystore localhost.truststore'
            subprocess.run(cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        for ip in self.conf_data['ENVIRONMENT']['ips']:
            user, path = get_username_path(self.conf_data, ip)
            port = self.conf_data['ENVIRONMENT'][
                'ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(ip)]
            file = os.path.abspath(
                self.path + '/scripts/temp/localhost.truststore')
            execute(put_file_remote,
                    localpath=file,
                    remotepath=os.path.abspath(path + '/localhost.truststore'),
                    hosts=user + '@' + ip + ':' + port)
        os.chdir(cwd)
        try:
            shutil.rmtree(self.path + '/scripts/temp')
        except:
            pass
        for node in self.conf_data['GATEWAY']['ips']:
            user, path = get_username_path(self.conf_data, node)
            cmd = path + '/jre/bin/keytool -importkeystore -noprompt -srckeystore ' +\
                path + '/localhost.truststore -destkeystore ' +\
                path + '/jre/' + 'lib/security/jssecacerts -srcstorepass ' +\
                'changeit -deststorepass changeit'
            fab_ob = using_fabric.AppviewxShell([node], user=user)
            ps = fab_ob.run(cmd)
            stat, res = return_status_message_fabric(ps)
            if not stat:
                lggr.error('Unable to merge localhost.truststore to jssecacerts on: ' + node)

if __name__ == '__main__':
    try:
        try:
            user_input = sys.argv
            ip = user_input[1]
        except:
            ip = False
        obj = InitializePlugins(ip)
        obj.initialize()
        print(colored('Plugins Initialized', 'green'))
        lggr.info('Plugins Initialized')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
