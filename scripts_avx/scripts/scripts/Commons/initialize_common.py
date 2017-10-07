#!../../Python/bin/python
"""File to initialize the common components across the nodes."""
import os
import socket
import sys
import subprocess
from termcolor import colored
import logger
import using_fabric
from configobj import ConfigObj
from avx_commons import port_status, primary_db
from avx_commons import check_accessibility
from avx_commons import execute_on_particular_ip
from avx_commons import return_status_message_fabric
from avx_commons import get_username_path
from using_fabric import AppviewxShell
from avx_commons import return_status_message_fabric
import avx_commons
import signal
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(current_file_path + '/../upgrade'))
lggr = logger.avx_logger('initialize_common')
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def help_fun():
        print(" ERROR in user_input:")
        print(
            " \t\t ./appviewx --initialize all/database/plugins/gateway/web")
        sys.exit(1)


class InitializeCommon():
    """The class to initialize common components."""

    def __init__(self, ip=False):
        """init."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.ip = ip
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.multinode = self.conf_data['ENVIRONMENT']['multinode'][0]
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def accessibility(self):
        """Check in case of multinode if all the nodes are accessible."""
        try:
            if self.conf_data['ENVIRONMENT'][
                    'multinode'][0].upper() == 'FALSE':
                return True

            node_details = []
            for username, ip in zip(self.conf_data['ENVIRONMENT']['username'],
                                    self.conf_data['ENVIRONMENT']['ips']):
                node_details.append(username + '@' + ip)
            status = check_accessibility(node_details, self.conf_data)
            if not status:
                print('Process Terminated!')
                sys.exit(1)
            lggr.debug('accessibility check completed')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def get_hostnames(self):
        """Get hostnames of all nodes and store in a file."""
        import json
        from avx_commons import get_username_path
        ip_hostname_dic = {}
        for node in self.conf_data['ENVIRONMENT']['ips']:
            cmd_for_hostname = 'hostname -f'
            user, path = get_username_path(self.conf_data, node)
            command = AppviewxShell([node], user=user)
            f_ob = command.run(cmd_for_hostname)
            stat, res = return_status_message_fabric(f_ob)
            if stat:
                ip_hostname_dic[node] = res
            else:
                ip_hostname_dic[node] = 'undefined'
        ip_hostname_dic = json.dumps(ip_hostname_dic)
        with open(current_file_path + '/../../properties/hostnames.txt', 'w+') as hosts:
            hosts.write(ip_hostname_dic)
        hosts = self.conf_data['ENVIRONMENT']['ips']
        hosts.remove(self.hostname)
        for node in self.conf_data['ENVIRONMENT']['ips']:
            user, path = get_username_path(self.conf_data, node)
            command = AppviewxShell([node], user=user)
            command.file_send(
                current_file_path + '/../../properties/hostnames.txt',
                path + '/properties/hostnames.txt')

    def log4j_level(self):
        """Initialize log4j."""
        try:
            components_list = ['WEB']
            for component in components_list:
                if self.conf_data[component][
                        'log_plus_access'][0].upper() == 'FALSE':

                    if self.ip:
                        path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                        log_4j_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/log4j_log_level.py ' + component + ' >/dev/null'
                        execute_on_particular_ip(self.conf_data, self.ip, log_4j_cmd)
                        return

                    for ip in self.conf_data['ENVIRONMENT']['ips']:
                        user, path = get_username_path(self.conf_data, ip)
                        log_4j_cmd = path + '/Python/bin/python ' + path + \
                            '/scripts/Commons/log4j_log_level.py ' + component + ' >/dev/null'
                        command = using_fabric.AppviewxShell([ip], user=user)
                        f_obj = command.run(log_4j_cmd)
                        status, res = return_status_message_fabric(f_obj)
                        if not status:
                            lggr.error('system components not configured on: ' + ip)
                        else:
                            lggr.debug('system components configured on: ' + ip)
                else:
                    log_elk_cmd = self.path + '/Python/bin/python ' + self.path + \
                        '/scripts/Commons/log4j_elk.py ' + component + ' >/dev/null'
                    if self.ip:
                        path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                        log_elk_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/log4j_elk.py ' + component + ' >/dev/null'
                        execute_on_particular_ip(self.conf_data, self.ip, log_elk_cmd)
                        return
                    for ip in self.conf_data['ENVIRONMENT']['ips']:
                        user, path = get_username_path(self.conf_data, ip)
                        log_elk_cmd = path + '/Python/bin/python ' + path + \
                            '/scripts/Commons/log4j_elk.py ' + component + ' >/dev/null'
                        command = using_fabric.AppviewxShell([ip], user=user)
                        f_obj = command.run(log_elk_cmd)
                        status, res = return_status_message_fabric(f_obj)
                        if not status:
                            lggr.error('system components not configured on: ' + ip)
                        else:
                            lggr.debug('system components configured on: ' + ip)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def system_components(self):
        """Initialize system_components."""
        try:
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                system_components_file_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/system_components.py'
                execute_on_particular_ip(self.conf_data, self.ip, system_components_file_cmd)
                return

            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                system_components_file_cmd = path + '/Python/bin/python ' + \
                    path + '/scripts/Commons/system_components.py'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(system_components_file_cmd)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('system components not configured on: ' + ip)
                else:
                    lggr.debug('system components configured on: ' + ip)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def crontab_configure(self):
        """Initialize crontab."""
        try:
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                crontab_configure_file_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/crontab_configure_python.py ' + self.path + ' >/dev/null'
                execute_on_particular_ip(self.conf_data, self.ip, crontab_configure_file_cmd)
                return

            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                crontab_configure_file_cmd = self.path + '/Python/bin/python ' + path + \
                    '/scripts/Commons/crontab_configure_python.py ' + path + ' >/dev/null'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(crontab_configure_file_cmd)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('Crontab not configured on: ' + ip)
                else:
                    lggr.debug('Crontab configured on: ' + ip)

        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def update_property_file(self):
        """Update property file."""
        try:
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                update_property_file_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/update_property_file.py >/dev/null'
                execute_on_particular_ip(self.conf_data, self.ip, update_property_file_cmd)
                return

            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                update_property_file_cmd = path + '/Python/bin/python ' + \
                    path + '/scripts/Commons/update_property_file.py >/dev/null'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(update_property_file_cmd)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('appviewx.properties not created on: ' + ip)
                else:
                    lggr.debug('appviewx.properties created on: ' + ip)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def java_security(self):
        """Initialize java security."""
        try:
            if self.ip:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                java_security_file_cmd = path + '/Python/bin/python ' + path + '/scripts/Commons/java_security_python.py >/dev/null'
                execute_on_particular_ip(self.conf_data, self.ip, java_security_file_cmd)
                return

            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                java_security_file_cmd = path + '/Python/bin/python ' + \
                    path + '/scripts/Commons/java_security_python.py >/dev/null'
                command = using_fabric.AppviewxShell([ip], user=user)
                f_obj = command.run(java_security_file_cmd)
                status, res = return_status_message_fabric(f_obj)
                if not status:
                    lggr.error('Java security not created on: ' + ip)
                else:
                    lggr.debug('Java security created on: ' + ip)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def load_balancer(self):
        """."""
        try:
            try:
                primary_db_ip_port = primary_db(self.conf_data)
                db_ip, db_port = primary_db_ip_port.split(':')
                result = port_status(db_ip, db_port)
                if 'listening' not in result:
                    raise Exception
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                sys.exit(1)
            except Exception as e:
                print (e)
                print (colored('Couldnt fetch primary db details', 'red'))
                sys.exit(1)
            path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            load_balancer_file_cmd = path + '/Python/bin/python ' \
                + path + '/scripts/Commons/push_lb.py ' \
                + path + ' ' + db_ip + ' ' + db_port + ' >/dev/null'
            to_push = 'True'
            if to_push:
                subprocess.run(load_balancer_file_cmd, shell=True)
            else:
                return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def check_certificates(self):
        """."""
        try:
            external_cert = self.conf_data['SSL']['external_certificate'][0]
            if external_cert.upper() == 'FALSE':
                ips = self.conf_data['ENVIRONMENT']['ips']
                usernames = self.conf_data['ENVIRONMENT']['username']
                paths = self.conf_data['ENVIRONMENT']['path']

                if self.ip:
                    path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.ip)]
                    cmd_to_gen_cert = path + '/Python/bin/python ' + \
                        current_file_path + '/self_signed_certificates.py >/dev/null'
                    execute_on_particular_ip(self.conf_data, self.ip, cmd_to_gen_cert)
                    return
                ips = self.conf_data['GATEWAY']['ips']
                for ip in ips:
                    user, path = get_username_path(self.conf_data, ip)
                    cmd_to_gen_cert = path + '/Python/bin/python ' + path + '/scripts/Commons/self_signed_certificates.py >/dev/null'
                    command = using_fabric.AppviewxShell([ip], user=user)
                    f_obj = command.run(cmd_to_gen_cert)
                    status, res = return_status_message_fabric(f_obj)
                    if not status:
                        lggr.error('self signed certs not created on: ' + ip)
                    else:
                        lggr.debug('Self signed certificates created on: ' + ip)
            else:
                ips = self.conf_data['GATEWAY']['ips']
                for ip in ips:
                    user, path = get_username_path(self.conf_data, ip)
                    cmd_to_gen_cert = path + '/Python/bin/python ' + path + '/scripts/Commons/self_signed_certificates.py already exists >/dev/null'
                    command = using_fabric.AppviewxShell([ip], user=user)
                    f_obj = command.run(cmd_to_gen_cert)
                    status, res = return_status_message_fabric(f_obj)
                    if not status:
                        lggr.error('self signed certs not created on: ' + ip)
                    else:
                        lggr.debug('Self signed certificates created on: ' + ip)

            web_cert = self.conf_data['SSL']['ssl_web_key'][0].replace('{appviewx_dir}', self.path)
            gateway_cert = self.conf_data['SSL']['ssl_gateway_key'][0].replace('{appviewx_dir}', self.path)

            self.validate_certificates('web', web_cert)
            self.validate_certificates('gateway', gateway_cert)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit()

    def validate_certificates(self, component, certificate):
        """."""
        try:
            field = component + '_key_password'
            password = self.conf_data['SSL'][field][0]
            cmd = 'openssl pkcs12 -in ' + certificate + ' -out temp.pem -password pass:' + password + ' -nodes'
            process = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            output = process.stderr.decode().strip()
            try:
                os.remove('temp.pem')
            except:
                pass
            if 'MAC verified OK'.lower() in output.lower():
                lggr.debug('Certificate verified for ' + component)
                return True
            else:
                lggr.debug('Certificate not verified for ' + component)
                return False
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def check_if_certs_exists(self):
        """."""
        try:
            certs = [self.path + '/server.key',
                     self.path + '/server.csr',
                     self.path + '/server.crt',
                     self.conf_data['SSL']['ssl_gateway_key'][0].replace('{appviewx_dir}', self.path),
                     self.conf_data['SSL']['ssl_web_key'][0].replace('{appviewx_dir}', self.path)]
            for file in certs:
                status = os.path.isfile(file)
                if status is False:
                    lggr.debug('One or more certificate files not found at their locations.')
                    return True
            lggr.debug('All certificate files found at their locations.')
            return False
        except Exception as e:
            print(e)
            lggr.error(e)
            sys.exit(1)

    def check_if_certs_to_be_generated(self):
        """."""
        try:
            property_file = self.path + '/properties/appviewx.properties'
            status = self.check_if_certs_exists()
            return status
            lggr.debug('No https conversion detected.')
            lggr.debug('No certificate files will be formed.')
            return False
        except Exception as e:
            print(e)
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """Initialize all components one by one."""
        try:
            self.accessibility()
            self.log4j_level()
            self.crontab_configure()
            self.update_property_file()
            self.java_security()
            to_gen = self.check_if_certs_to_be_generated()
            if to_gen:
                web_https = self.conf_data['WEB']['appviewx_web_https'][0].upper()
                gateway_https = self.conf_data['GATEWAY']['appviewx_gateway_https'][0].upper()
                if web_https == 'TRUE' or gateway_https == 'TRUE':
                    self.check_certificates()
            self.get_hostnames()
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def update_db(self):
        """Initialize all components one by one."""
        try:
            from dependency_check import get_plugin_details
            self.system_components()
            self.load_balancer()
            get_plugin_details()
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
        obj = InitializeCommon(ip)
        obj.initialize()
        print(colored('Common components initialized.', 'green'))
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
