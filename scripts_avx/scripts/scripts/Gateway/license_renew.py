#!../../Python/bin/python
"""."""
import os
import sys
import socket
import subprocess
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
sys.path.insert(0, current_file_path + '/../Web')
import gateway
import web
import logger
lggr = logger.avx_logger('license_renew')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def help_fun():
    """Help function.

    help_fun display text to guide user.
    incase of invalid arguments given
    by user or upon request

    """
    print("""\n    usage: ./appviewx --license [argument] \n \
     options:\n \
     \t renew \t \t renewal of license \n \

    example: """ + colored("""\n \
     \t 1. appviewx --license  renew <licencefile>""", 'blue'))

    return True


class LicenseRenewal():
    """."""

    def __init__(self, license):
        """."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            self.multinode = self.conf_data['ENVIRONMENT']['multinode'][0]
            self.license = license
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def remove_old_license(self):
        """."""
        try:
            list_of_cmds = []
            if self.multinode.upper() == 'FALSE':
                cmd = 'rm -rf ' + self.path + '/avxgw/*'
                list_of_cmds.append(cmd)
            else:
                for dest in self.conf_data['ENVIRONMENT']['ssh_hosts']:
                    node, path = dest.split(':')
                    conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(node.split('@')[1])]
                    conn_port = str(conn_port)
                    cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + node + ' "rm -rf ' + path + '/avxgw/*' + '"'
                    list_of_cmds.append(cmd)
            return list_of_cmds
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def copy_license_file(self):
        """."""
        try:
            list_of_cmds = []
            if self.multinode.upper() == 'FALSE':
                cmd = 'rsync -avz ' + self.license + ' ' + self.path + '/avxgw/'
                list_of_cmds.append(cmd)
                return list_of_cmds
            else:
                for dest in self.conf_data['ENVIRONMENT']['ssh_hosts']:
                    conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(dest.split(':')[0].split('@')[1])]
                    conn_port = str(conn_port)
                    cmd = 'rsync  -avz -e \"ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + '\" ' + self.license + ' ' + dest + '/avxgw/'
                    list_of_cmds.append(cmd)
                return list_of_cmds
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def extract_license_file(self):
        """."""
        try:
            list_of_cmds = []
            file = self.license.split('/')[-1]
            if self.multinode.upper() == 'FALSE':
                cmd = 'cd ' + self.path + '/avxgw/ && tar -xvf ' + self.path + '/avxgw/' + file
                list_of_cmds.append(cmd)
                return list_of_cmds
            else:
                for dest in self.conf_data['ENVIRONMENT']['ssh_hosts']:
                    node, path = dest.split(':')
                    conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(node.split('@')[1])]
                    conn_port = str(conn_port)
                    cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + node + ' "cd ' + path + '/avxgw/ && tar -xvf ' + path + '/avxgw/' + file + '"'
                    list_of_cmds.append(cmd)
                return list_of_cmds
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def run_role_management(self):
        """."""
        try:
            list_of_cmds = []
            properties_path = self.path + '/properties/'
            acf_admin_jar_path = self.path + '/avxgw/acf-admin-1.0.0.jar'
            cmd = self.path + '/jre/bin/java -Davx_logs_home=' + self.path + '/logs/acf-admin.logs -cp ' + acf_admin_jar_path + ':'+ self.path + '/Plugins/framework/framework-db.jar:' +  properties_path + ' com.appviewx.acfadmin.main.AcfAdminMain'
            if not os.path.isfile(self.path + '/Plugins/framework/framework-db.jar'):
                lggr.error('framework-db.jar is missing in directory ' + self.path + '/Plugins/framework')
                print (colored('framework-db.jar is missing in directory ' + self.path + '/Plugins/framework.So acf-admin.jar is not executing'),'red')
                return
            list_of_cmds.append(cmd)
            # print (cmd)
            return list_of_cmds
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def remove_role_managment_jar(self):
        """."""
        try:
            list_of_cmds = []
            if self.multinode.upper() == 'FALSE':
                cmd = 'rm -rf ' + self.path + '/avxgw/RoleTemplateMgmt.jar'
                list_of_cmds.append(cmd)
                return list_of_cmds
            else:
                for dest in self.conf_data['ENVIRONMENT']['ssh_hosts']:
                    node, path = dest.split(':')
                    conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(node.split('@')[1])]
                    conn_port = str(conn_port)
                    cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + node + ' "rm -rf ' + path + '/avxgw/RoleTemplateMgmt.jar' + '"'
                    list_of_cmds.append(cmd)
                return list_of_cmds
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def execute_command(cmd_list):
        """."""
        for cmd in cmd_list:
            try:
                ps = subprocess.run(cmd + ' > /dev/null 2>&1', shell=True)
                lggr.debug('Executed command: ' + cmd)
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                print(e)
                sys.exit(1)
        return ps.returncode

    def renew(self):
        """."""
        try:
            path_of_license_folder = os.path.abspath(self.path + '/avxgw')
            license = os.path.abspath(self.license)
            if path_of_license_folder in license:
                print('The license cannot be in the avxgw folder!')
                lggr.error('Path of the license is invalid. The license file cannot be present in the avxgw field!')
                sys.exit(1)

            # Remove old license
            cmd_list = self.remove_old_license()
            lggr.info('Removing old license')
            self.execute_command(cmd_list)

            # copy new license
            cmd_list = self.copy_license_file()
            lggr.info('Copying new license')
            self.execute_command(cmd_list)

            # extract new license
            cmd_list = self.extract_license_file()
            lggr.info('Extracting new license')
            self.execute_command(cmd_list)

            # run role management jar
            cmd_list = self.run_role_management()
            lggr.info('Running role management jar')
            err_code = self.execute_command(cmd_list)

            # initialize
            from initialize_gateway import InitializeGateway
            obj = InitializeGateway()
            obj.initialize()
            lggr.info('Gateway Initialized')
            from initialize_common import InitializeCommon
            obj = InitializeCommon()
            obj.update_property_file()
            lggr.info('Property file updated')

            print('License Renewal Completed.')
            lggr.info('License Renewed')

            # restart service and gateway if required
            lggr.debug('Restarting Gateway')
            operation = ['--restart', 'gateway']
            gateway_obj = gateway.Gateway(operation, self.conf_data)
            gateway_obj.operation()
        except KeyboardInterrupt:
            print(colored('\nKeyboard Interrupt', 'red'))
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

if __name__ == '__main__':
    try:
        user_input = sys.argv
        if not len(user_input) == 2:
            print('license renew file takes exactly one arguement!')
            print('path to license file')
            print('exiting!!')
            sys.exit(1)
        license = os.path.abspath(user_input[1])
        if not license.endswith('license.tar.gz'):
            print('The license file is not a valid file!')
            lggr.debug('The license file is not a valid file!')
            lggr.error('The license file is not a valid file!')
            sys.exit(1)

        ob = LicenseRenewal(license)
        print('License Renewal Started.')
        lggr.info('License Renewal Started')
        ob.renew()
        lggr.info('License renew completed')

    except KeyboardInterrupt:
        print(colored('\nKeyboard Interrupt', 'red'))
        sys.exit(1)
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
