#!Python/bin/python
"""."""
import warnings
warnings.filterwarnings("ignore")
import warnings
warnings.filterwarnings("ignore")
import os
import sys
import socket
import subprocess
import glob
import readline
from threading import Thread
from termcolor import colored
import psutil
import logging
import shutil
import math
from fabric.api import *
import fabric
import getpass
import signal

current_file_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostbyname(socket.gethostname())
logger = logging.getLogger('Installer')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('install.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s\t%(message)s', '%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
prerequisite_status_check = []
prerequisite_port_check = []
date_check = dict()
time_check = dict()
zone_time_check = dict()
UTC_list = dict()
seconds_list = list()
prereq_str = str()
change = str()
in_path = str()
warn_str = str()


def key_int(signal, frame):
    """Handle Keyboard Interrupt."""
    sys.exit(1)

signal.signal(signal.SIGINT, key_int)


def complete(text, state):
    """."""
    return (glob.glob(text + '*') + [None])[state]


def either(c):
    """."""
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


class Bcolors:
    """."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[95m'


class AppviewxShell(object):
    """Custom class with fabric to execute all the remote commands for AppViewX scripts."""

    def __init__(self, hostname=None, cmd=None, user=None, pty=True, port=22, parallel=False):
        """Host and user details are stored for fabric execution."""
        """@param hostname type: List
        @param hostname: List of ip address"""

        if hostname:
            env.hosts = hostname
        if user:
            env.user = user
        else:
            env.user = 'appviewx'
        self.pty = pty
        env.port = port
        # fabric output would be suppressed
        fabric.state.output['running'] = False
        fabric.state.output['output'] = False
        self.cmd = cmd
        self.parallel = parallel
        if parallel:
            env.parallel = True
        else:
            env.parallel = False

    def _exec_remote_cmd(self):
        """Private function to execute the command with the default settings."""
        """Not to be used by the external system"""
        try:
            with hide('warnings'), settings(warn_only=True, parallel=self.parallel, capture=True):
                if env.hosts[0] == hostname and env.user == getpass.getuser() and len(env.hosts) == 1:
                    result = local(self.cmd, capture=True)
                else:
                    if self.pty:
                        result = run(self.cmd)
                    else:
                        result = run(self.cmd, pty=self.pty)
                return result, result.succeeded
        except Exception:
            raise Exception

    def run(self, cmd, user='appviewx'):
        """The function to be called with an object to execute the command."""
        try:
            self.cmd = cmd
            self.result = execute(self._exec_remote_cmd)
            status = list(self.result.values())[-1][-1]
            res = list(self.result.values())[-1][0]
            return res, status
        except Exception:
            raise Exception

    def _file_send(self):
        try:
            result = put(
                self.localpath,
                self.remotepath,
                mirror_local_mode=True)
            if result.succeeded:
                return 'Success'
            else:
                return 'Failed'
        except Exception:
            return 'Error'

    def file_send(self, localpath, remotepath):
        """."""
        try:
            self.localpath = localpath
            self.remotepath = remotepath
            try:
                self.result = execute(self._file_send)
            except:
                print('Some problem in sending the file: ' + localpath + ' to ' + env.hosts[0])
            result = []
            for k, v in self.result.items():
                result.append(k + ':' + v + '\n')
            return ''.join(result)

        except Exception as e:
            print(e)


class InstallAVX():
    """The Class to install AppViewX."""

    def __init__(self):
        """."""
        try:
            self.hostname = socket.gethostbyname(socket.gethostname())
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def print_format(first_value, second_value, key_color='white', value_color='green', third_color='green', third_value=''):
        """."""
        try:
            global prereq_str
            prereq_str += '\n' + '{0:7s} {1:35s} {2:7s} {3:40s} {4:20s}'.format(
                ' ', colored(first_value, key_color), ':', colored(second_value, value_color), colored(third_value, third_color))
        except KeyboardInterrupt:
            sys.exit(1)

    def system_check(self, ip):
        """."""
        try:
            global prereq_str
            global warn_str
            conn_port = conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(ip)]
            username = conf_data['ENVIRONMENT']['username'][conf_data['ENVIRONMENT']['ips'].index(ip)]
            conn_port = str(conn_port)
            Bcolors.OKBLUE
            fab_ob = AppviewxShell([ip], user=username, port=conn_port)
            cmd = ''
            host_ip_add, status = fab_ob.run(cmd + "hostname -i 2> /dev/null")
            prereq_str += '\n' + "\thost-ip\t\t\t   :   \t" + str(host_ip_add.strip())
            host_name_info, status = fab_ob.run(cmd + "hostname 2> /dev/null")
            prereq_str += '\n' + "\thostname\t\t   :   \t" + host_name_info.strip()
            system_date_info, status = fab_ob.run(cmd + "date +%Y/%m/%d 2> /dev/null")
            date_val = system_date_info.strip()
            date_check[ip] = date_val
            prereq_str += '\n' + "\tdate\t\t\t   :   \t" + date_val
            system_time_info, status = fab_ob.run(cmd + "date +%H:%M:%S 2> /dev/null")
            time_val = system_time_info.strip()
            time_check[ip] = time_val
            prereq_str += '\n' + "\ttime\t\t\t   :   \t" + time_val
            system_zone_time_info, status = fab_ob.run(cmd + "date +%Z 2> /dev/null")
            zone_time_val = system_zone_time_info.strip()
            zone_time_check[ip] = zone_time_val
            UTC_list[ip], status = fab_ob.run(cmd + 'date -u 2> /dev/null')
            Bcolors.ENDC
            prereq_str += '\n' + colored("\tPrerequisite\t\t   :   \tRecommended\t\t   :   \tAvailablity", 'blue')
            warn_str += colored("\tPrerequisite\t\t   :   \tRecommended\t\t   :   \tAvailablity", 'blue')
            operating_system_str, status = fab_ob.run(cmd + " python -mplatform 2>/dev/null")
            operating_system = operating_system_str.split('-')[-3]
            os_version = operating_system = operating_system_str.split('-')[-2]
            prereq_str += '\n' + "\toperating system\t   :   \tRedHat/CentOs\t\t   :   \t" + (operating_system)
            no_of_cpu = psutil.cpu_count()
            if no_of_cpu < 8:
                no_of_cpu = Bcolors.FAIL + str(no_of_cpu) + Bcolors.ENDC
                warn_str += '\n' + "\tnumber of cpus\t\t   :   \t8\t\t\t   :   \t" + str(no_of_cpu)
            prereq_str += '\n' + "\tnumber of cpus\t\t   :   \t8\t\t\t   :   \t" + str(no_of_cpu)
            architecture, status = fab_ob.run(cmd + "lscpu 2> /dev/null | grep Architecture | awk '{print $2}'")
            if 'x86_64' not in architecture:
                architecture = Bcolors.FAIL + architecture + Bcolors.ENDC
                warn_str += '\n' + "\tarchitecture\t\t   :   \tx86_64\t\t\t   :   \t" + str(architecture)
            prereq_str += '\n' + "\tarchitecture\t\t   :   \tx86_64\t\t\t   :   \t" + str(architecture)
            total_memory, status = fab_ob.run(cmd + " free -m 2> /dev/null | grep \"Mem\" |awk '{ print($2/1024) }' ")
            total_memory = int(math.ceil(float(total_memory.strip())))
            if total_memory < 16:
                total_memory = Bcolors.FAIL + str(total_memory) + Bcolors.ENDC
                warn_str += '\n' + "\ttotal ram memory\t   :   \t16GB\t\t\t   :   \t" + str(total_memory)
            prereq_str += '\n' + "\ttotal ram memory\t   :   \t16GB\t\t\t   :   \t" + str(total_memory)
            free_memory, status = fab_ob.run(cmd + " free -m 2> /dev/null | grep \"Mem\" | awk '{ printf($4/1024)}' ")
            free_memory = int(math.ceil(float(free_memory.strip())))
            if free_memory < 16:
                free_memory = Bcolors.FAIL + str(free_memory) + Bcolors.ENDC
            prereq_str += '\n' + "\tfree ram memory\t\t   :   \t16GB\t\t\t   :   \t" + str(free_memory)
            free_disk_space, status = fab_ob.run(cmd + "df -Ph . 2> /dev/null | tail -1 | awk '{print $4}'")
            free_disk_space = int(float(free_disk_space.strip().strip('G').strip('M')))
            if free_disk_space < 200:
                free_disk_space = Bcolors.FAIL + str(free_disk_space) + Bcolors.ENDC
                warn_str += '\n' + "\tfree disk space\t\t   :   \t200GB\t\t\t   :   \t" + str(free_disk_space)
            prereq_str += '\n' + "\tfree disk space\t\t   :   \t200GB\t\t\t   :   \t" + str(free_disk_space)
            ulimit_value_file, status = fab_ob.run(cmd + "ulimit -n 2> /dev/null")
            ulimit_value_file = int(ulimit_value_file.strip())
            if ulimit_value_file < 65535:
                ulimit_value_file = Bcolors.FAIL + str(ulimit_value_file) + Bcolors.ENDC
                warn_str += '\n' + "\topen files[ulimit -n]\t   :   \t65535\t\t\t   :   \t" + str(ulimit_value_file)
            prereq_str += '\n' + "\topen files[ulimit -n]\t   :   \t65535\t\t\t   :   \t" + str(ulimit_value_file)
            ulimit_value_process, status = fab_ob.run(cmd + "ulimit -u 2> /dev/null")
            ulimit_value_process = int(ulimit_value_process.strip())
            if ulimit_value_process < 65535:
                ulimit_value_process = Bcolors.FAIL + str(ulimit_value_process) + Bcolors.FAIL
                warn_str += '\n' + "\tmax processes[ulimit -u]   :   \t65535\t\t\t   :   \t" + str(ulimit_value_process)
            prereq_str += '\n' + "\tmax processes[ulimit -u]   :   \t65535\t\t\t   :   \t" + str(ulimit_value_process)
            prereq_str += ''
            self.print_format('Packages', 'Availability', key_color='blue', value_color='blue')
            packages = ['nc', 'nmap-ncat', 'nmap', 'curl', 'sysstat', 'tcpdump', 'rsync', 'lsof', 'openssl']
            if os_version.startswith('6'):
                packages.remove('nmap-ncat')
            nc_check = 0
            not_installed_package = list()
            for package in packages:
                cmd = 'rpm -ql ' + package
                k, status = fab_ob.run(cmd)
                if 'not installed' in k:
                    if package == 'nc':
                        nc_check = 1
                    elif package == 'nmap-ncat':
                        if nc_check == 1:
                            not_installed_package.append(package)
                    else:
                        not_installed_package.append(package)
            for i in packages:
                if i in not_installed_package:
                    self.print_format(
                        i,
                        'Package not installed',
                        value_color='red')
                    prerequisite_status_check.append('package')
                else:
                    self.print_format(
                        i,
                        'installed')
        except KeyboardInterrupt:
            sys.exit(1)

    @staticmethod
    def port_status(ip, port):
        """."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            try:
                result = sock.connect_ex((ip, int(port)))  # socket connection
            except Exception:
                return "not_reachable"
            sock.close()
            if result == 0:
                return "listening"
            return "open"
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception:
            raise Exception

    def port_check(self, conf_data, ip=None):
        """."""
        global prereq_str
        try:
            if ip is None:
                ip = socket.gethostbyname(socket.gethostname())

            components = ['mongodb', 'gateway', 'web']
            port_list = list()
            final_status = True
            port_list.append(int(conf_data['COMMONS']['scheduler_port'][0]))
            prereq_str += ''
            self.print_format(
                "Port",
                "Status",
                key_color='blue',
                value_color='blue')
            for component in components:
                try:
                    component_ips = conf_data[component.upper()]['ips']
                    component_ports = conf_data[component.upper()]['ports']
                except KeyError:
                    continue
                ports_index = [
                    index for index,
                    value in enumerate(component_ips) if value == ip]
                for index in ports_index:
                    port_list.append(component_ports[index])
            for port in port_list:
                ip_port_status = self.port_status(ip, port)
                if ip_port_status == 'listening':
                    prerequisite_port_check.append(port)
                    self.print_format(port, ip_port_status, value_color='red')
                    final_status = False
                else:
                    self.print_format(port, ip_port_status)
            components = conf_data['PLUGINS']['plugins']
            port_list = list()
            for component in components:
                try:
                    component_ips = conf_data['PLUGINS'][component.lower()][
                        'ips']
                    component_ports = conf_data['PLUGINS'][component.lower()][
                        'ports']
                except KeyError:
                    continue
                ports_index = [
                    index for index,
                    value in enumerate(component_ips) if value == ip]
                for index in ports_index:
                    port_list.append(component_ports[index])
            for port in port_list:
                ip_port_status = self.port_status(ip, port)
                if ip_port_status == 'listening':
                    self.print_format(port, ip_port_status, value_color='red')
                    prerequisite_port_check.append(port)
                    final_status = False
                else:
                    self.print_format(port, ip_port_status)
            return final_status
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def execute_cmd(cmd, ip=None):
        """."""
        try:
            if not ip:
                ip = socket.gethostbyname(socket.gethostname())
            conn_port = conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(ip)]
            username = conf_data['ENVIRONMENT']['username'][conf_data['ENVIRONMENT']['ips'].index(ip)]
            fab_ob = AppviewxShell([ip], user=username, port=conn_port)
            ps, status = fab_ob.run(cmd)
            return status
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def execute_parallely(self, cmds):
        """."""
        try:
            thread_list = []
            for cmd in cmds:
                thread_list.append(
                    Thread(target=self.execute_cmd, args=(cmd,)))
            for threads in thread_list:
                threads.start()
            while True:
                thread_status = [x.isAlive() for x in thread_list]
                if not any(thread_status):
                    break
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def execute_serially(cmds):
        """."""
        try:
            for cmd in cmds:
                subprocess.run(cmd + ' &>/dev/null', shell=True)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def copy_file(file_to_copy, file_type, node_details, conf_data, instance=None):
        """To copy files."""
        try:
            cmds_to_return = []
            if file_type == 'installer':
                for node in node_details:
                    dest = node.split(':')[1]
                    host, path = node.split(':')
                    if host.split('@')[1] == hostname:
                        cmd = 'rsync -avz ' + file_to_copy + ' ' + dest
                    else:
                        conn_port = str(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])])
                        cmd = 'rsync -avz -e \"ssh -oStrictHostKeyChecking=no -p ' + conn_port + '\"  ' + file_to_copy + ' ' + node
                    cmds_to_return.append(cmd)
            elif file_type == 'license':
                for node in node_details:
                    dest = node.split(':')[1] + '/avxgw'
                    host, path = node.split(':')
                    if host.split('@')[1] == hostname:
                        cmd = 'rsync -avz ' + file_to_copy + ' ' + dest
                    else:
                        conn_port = str(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])])
                        cmd = 'rsync -avz -e \" ssh -oStrictHostKeyChecking=no -p ' + conn_port + '\"  ' + file_to_copy + ' ' + node + '/avxgw'
                    cmds_to_return.append(cmd)
            elif file_type == 'conf':
                for node in node_details:
                    dest = node.split(':')[1] + '/conf'
                    host, path = node.split(':')
                    if host.split('@')[1] == hostname:
                        cmd = 'rsync -avz ' + file_to_copy + ' ' + dest
                    else:
                        conn_port = str(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])])
                        cmd = 'rsync -avz -e \"ssh -oStrictHostKeyChecking=no -p ' + conn_port + '\"  ' + file_to_copy + ' ' + node + '/conf'
                    cmds_to_return.append(cmd)
            return cmds_to_return
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def extract_tar(file_name, file_type, node_details, conf_data, instance=None):
        """.To extract installer and license."""
        try:
            cmds_to_return = []
            file_name = file_name.split('/')[-1]
            if file_type == 'installer':
                for node in node_details:
                    dest = node.split(':')[1]
                    host, path = node.split(':')
                    if host.split('@')[1] == hostname:
                        cmd = 'cd ' + dest + ' && tar -xvf ' + file_name
                    else:
                        conn_port = str(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])])
                        cmd = 'ssh -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + host + ' "cd ' + path + ' && tar -xvf ' + file_name + '"'
                    cmds_to_return.append(cmd)
            elif file_type == 'license':
                for node in node_details:
                    dest = node.split(':')[1] + '/avxgw'
                    host, path = node.split(':')
                    if host.split('@')[1] == hostname:
                        cmd = 'cd ' + dest + ' && tar -xvf ' + file_name
                    else:
                        conn_port = str(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])])
                        cmd = 'ssh -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + host + ' "cd ' + path + '/avxgw && tar -xvf ' + file_name + '"'
                    cmds_to_return.append(cmd)
            return cmds_to_return
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def get_installer(self):
        """."""
        try:
            installer = input("Enter AppViewX installer path : ")

            update_installer = ''
            if not os.path.exists(installer):
                print('Not a valid installer path!')
                update_installer = self.get_installer()
            else:
                if (installer.lower().endswith('.zip') or
                        installer.lower().endswith('tar.gz') and
                        'AppViewX' in installer and
                        'license' not in installer):
                    print('Installer file validated.')
                    return installer
                else:
                    print('Invalid format! Installer should be tar/zip file.')
                    update_installer = self.get_installer()
            return update_installer
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def get_license(self):
        """."""
        try:
            license = input("Enter AppViewX license path : ")

            update_license = ''
            if not os.path.exists(license):
                print('Not a valid license path!')
                update_license = self.get_license()
            else:
                if license.lower().endswith('license.tar.gz'):
                    print('License file validated.')
                    return license
                else:
                    print('Invalid format! License should be license.tar.gz file.')
                    update_license = self.get_license()
            return update_license
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def get_config_file(self):
        """."""
        try:
            global change
            print('conf file not found!')
            try:
                choice = input(
                    'Do you want to proceed without conf file (Yes/No)?: ')
            except KeyboardInterrupt:
                sys.exit(1)

            if choice.upper() == 'NO':
                conf = input("Enter appviewx.conf path : ")

                update_conf = ''
                if not os.path.exists(conf):
                    print('Not a valid config file path!')
                    update_conf = self.get_config_file()
                else:
                    if conf.lower().endswith('.conf'):
                        print('Conf file validated.')
                        return conf
                    else:
                        print(
                            'Invalid format! Config file should be .conf file.')
                        update_conf = self.get_config_file()
                return update_conf
            elif choice.upper() == 'YES':
                change = 'yes'
                return ''
            else:
                print('Yes/No')
                self.get_config_file()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def get_files(self, flag):
        """Get installer, license and conf files."""
        try:
            license = glob.glob(''.join(map(either, '*license.tar.gz')))[0]
        except Exception:
            license = self.get_license()
        if not flag:
            try:
                installer = glob.glob(''.join(map(either, 'appviewx.zip')))[0]
            except Exception:
                try:
                    installer = glob.glob(
                        ''.join(map(either, 'appviewx.tar.gz')))[0]
                except Exception:
                    try:
                        installer = glob.glob('appviewx_*_installer.tar.gz')[0]
                    except Exception:
                        installer = self.get_installer()
        else:
            installer = ''
        try:
            conf_file = glob.glob('appviewx.conf')[0]
        except Exception:
            conf_file = self.get_config_file()

        return installer, license, conf_file

    def copy_rsa_value(self):
        """."""
        try:
            ssh_path = os.path.expanduser("~/.ssh/")
            rsa_path = ssh_path + 'id_rsa.pub'
            if os.path.exists(rsa_path):
                rsa_key = 'cat ' + ssh_path + 'id_rsa.pub >> ' + ssh_path + 'authorized_keys'
                change_mod = 'chmod og-wx ' + ssh_path + 'authorized_keys'
                cat_auth_key = self.execute_cmd(rsa_key)
                run_chmod = self.execute_cmd(change_mod)

                if not cat_auth_key:
                    print('Could not cat authorized keys')
                if not run_chmod:
                    print('Could not change mode of authorized_keys')
            else:
                print('%sauthorized_keys file not found.' % ssh_path)

        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    @staticmethod
    def get_node_details(conf_data=None):
        """."""
        try:
            node_details = conf_data['ENVIRONMENT']['ssh_hosts']
            return node_details
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def remove_existing_content(self, node_details, instance=None):
        """."""
        ssh_path = os.path.expanduser("~/.ssh/")
        if isinstance(node_details, str):
            nodes1 = []
            nodes1.append(node_details)
            node_details = nodes1

        if not os.path.exists("empty_directory"):
            os.makedirs("empty_directory")

        for node in node_details:
            try:
                conn_port = conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(node.split(':')[0].split('@')[1])]
                conn_port = str(conn_port)
                path = node.split(":")[1]
                ip = node.split('@')[-1].split(':')[0]

                cmd = 'mkdir -p ' + node.split(":")[1]
                try:
                    self.execute_cmd(cmd, ip)
                except:
                    print(
                        Bcolors.FAIL +
                        "Error in creating folder @" +
                        node.split(":")[0].split("@")[1] +
                        Bcolors.ENDC)
                    sys.exit(1)
                if os.path.exists(path):
                    if os.access(path, os.R_OK):
                        if os.access(path, os.W_OK):
                            logger.debug('write permission OK for ' + path)
                        else:
                            print(
                                "Write permission for installation path:%s is denied" %
                                path)
                            sys.exit(1)
                    else:
                        print(
                            "Read permission for installation path:%s is denied" %
                            path)
                        sys.exit(1)
                keyscan_cmd = 'ssh-keyscan ' + node.split(':')[0].split(
                    '@')[1] + '>> ' + ssh_path + 'known_hosts '
                if os.path.exists(ssh_path + 'known_hosts') and instance == 'multinde':
                    self.execute_cmd(keyscan_cmd)
                if instance == 'singlenode':
                    node = node.split(':')[-1]
                    cmd = 'rm -rf ' + node + '/*'
                else:
                    cmd = "ssh -oStrictHostKeyChecking=no " + node.split(':')[0] + " -p " + str(conn_port) + " 'rm -rf " + node.split(':')[1] + "/*'"
                ps = self.execute_cmd(cmd)
                if not ps:
                    sys.exit(1)
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                print(
                    'Could not delete the existing folder @%s. Error %s' %
                    (node, e))
                sys.exit(1)
        try:
            os.rmdir("empty_directory")
        except Exception:
            logger.error('error in deleting contents of directory')

    @staticmethod
    def check_parent(file, path):
        """."""
        try:
            if not file:
                return False

            path_of_file = os.path.realpath(file)
            path = os.path.abspath(path)
            if path_of_file.startswith(path + '/'):
                return 'invalid'
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def get_installation_path(self, list_of_files):
        """."""
        try:
            prompt = 'Installation Path '
            try:
                installation_path = input(prompt + ': ')
                if not installation_path.startswith('~'):
                    installation_path = os.path.abspath(installation_path)
            except KeyboardInterrupt:
                sys.exit(1)
            status = self.validation(list_of_files, installation_path, prompt_again=True)
            if status:
                global in_path
                in_path = installation_path
            else:
                self.get_installation_path(list_of_files)
        except Exception as e:
            print(e)
            sys.exit(1)

    def validation(self, list_of_files, installation_path, prompt_again=False):
        """."""
        try:
            flag = True
            if os.path.isfile(installation_path) or '.' in installation_path:
                print('Not a valid Installation Path')
                return False
                if prompt_again:
                    self.get_installation_path(list_of_files)
                else:
                    sys.exit(1)
            for file in list_of_files:
                validity = self.check_parent(file, installation_path)
                if validity == 'invalid':
                    print('Installation path cannot be a parent directory of the file')
                    flag = False
                    break
            current_dir = os.path.dirname(os.path.realpath(__file__))
            if installation_path == current_dir or installation_path == '.':
                print('Current directory and installation path can not be same!!')
                flag = False
            if installation_path.startswith('~'):
                print('Not a valid path! Path cannot start with a ~')
                flag = False
            if flag:
                return True
            if prompt_again and not flag:
                self.get_installation_path(list_of_files)
            elif not prompt_again and not flag:
                sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)


if __name__ == '__main__':
    if os.getuid() == 0:
        print('Root user is not allowed to install AppViewX')
        logger.error('Root user found. Exiting!')
        sys.exit(1)

    user_input = sys.argv
    installer = str()

    try:
        if len(user_input) == 1:
            logger.debug('Normal ./install.py called')
        elif len(user_input) == 2:
            if os.path.isfile(user_input[1]) and user_input[1].endswith('.tar.gz') and 'AppViewX' in user_input[1] and 'license' not in user_input[1]:
                installer = user_input[1]
        else:
            print('Usage:\n\tpython ' + __file__ + ' { installer_path }')
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

    ob = InstallAVX()
    from config_parser import config_parser

    print(
        colored(
            '*************************** Fresh installation started ****************************',
            'green'))
    logger.info(
        '*************************** Fresh installation started ****************************')

    # Get installer, license and conf files
    if installer:
        flag = True
        temp = installer
    else:
        flag = False
    installer, license, conf_file = ob.get_files(flag)
    if not len(installer):
        installer = temp

    ask = True

    if not conf_file:
        while True:
            try:
                choice = 'yes'
            except KeyboardInterrupt:
                sys.exit(1)
            if choice.lower() == 'yes':
                from configuration_generation import conf_file_generation
                conf_file_generation.conf_generate_start(conf_file_generation(), installer)
                ask = False
                change = 'False'
                conf_file = 'appviewx.conf'
                break
            elif choice.lower() == 'no':
                break

    logger.debug('Got files : ' + str(installer) + ' ' + str(license) + ' ' + str(conf_file))

    installation_path = False

    if not conf_file:
        instance = 'singlenode'
        cmd = 'tar -xf ' + installer + ' conf/appviewx.conf'
        try:
            subprocess.run(cmd, shell=True)
        except KeyboardInterrupt:
            sys.exit(1)
        conf_data = config_parser('conf/appviewx.conf')
        shutil.rmtree('conf/')
    else:
        conf_data = config_parser(conf_file)
        if conf_data['ENVIRONMENT']['multinode'][0].upper() == 'FALSE':
            instance = 'singlenode'
            if ask:
                installation_path = input('AppViewX installation path (Default: (' + conf_data['ENVIRONMENT']['path'][0] + '): ')
                if installation_path == '':
                    installation_path = conf_data['ENVIRONMENT']['path'][0]
            else:
                installation_path = conf_data['ENVIRONMENT']['path'][0]
        elif conf_data['ENVIRONMENT']['multinode'][0].upper() == 'TRUE':
            instance = 'multinode'
            installation_path = conf_data['ENVIRONMENT']['path'][conf_data['ENVIRONMENT']['ips'].index(hostname)]

    logger.debug('instance  = ' + instance)

    if instance == 'multinode':
        ob.copy_rsa_value()

    # Prerequiste check
    # Checking for packages and ports
    print('Starting Prerequisite check')
    to_exit = False
    for ip in conf_data['ENVIRONMENT']['ips']:
        logger.debug('Starting prerequisite check on ' + str(ip))
        ob.system_check(ip)
        ob.port_check(conf_data, ip)
        if len(prerequisite_status_check) or len(prerequisite_port_check):
            print(prereq_str)
            print(colored('Either a package is not installed or port is listening', 'red'))
            logger.debug('Prerequisite check failed!')
            to_exit = True
        elif len(warn_str) > 125:
            print(colored('The following system specifications are not upto mark for ' + ip + '.', 'yellow'))
            print(warn_str)
        else:
            print('{0:30s}  {1:15s}  {2:10s} {3:5s}'.format(' ', ip, '', colored('Success', 'green')))
            logger.debug('Prerequisite check successfull.')
        prereq_str = ''
        prerequisite_status_check = []
        prerequisite_port_check = []
        warn_str = ''
    if to_exit:
        sys.exit(1)

    list_of_files = [installer, license, conf_file]

    if installation_path:
        ob.validation(list_of_files, installation_path)
    else:
        ob.get_installation_path(list_of_files)
        installation_path = in_path

    if instance == 'multinode':
        node_details = ob.get_node_details(conf_data)
        node_path = [x.split(':')[1] for x in node_details if x.split('@')[1].split(':')[0] == hostname ]
        if len(node_path):
            path = node_path[0]
            if path == os.getcwd() or path == '.':
                print('Current directory and installation path can not be same!!')
                sys.exit(1)
        parent_dir = list()
        ins_dir = path
        while not ins_dir == '/':
            ins_dir = os.path.dirname(ins_dir)
            parent_dir.append(ins_dir)
        if path in parent_dir:
            print('Installation directory shouldnt be the parent directory of the current directory!!')
            sys.exit(1)
    elif instance == 'singlenode':
        installation_path = str(installation_path).strip()
        username_ip = socket.gethostbyname(socket.gethostname())
        username = getpass.getuser()
        nd_details = username + '@' + username_ip + ':' + installation_path
        node_details = [nd_details]
        instance = 'singlenode'

    ob.remove_existing_content(node_details, instance)

    try:
        parallel = conf_data['COMMONS']['parallel_execution'][0]
    except Exception as e:
        parallel = 'True'

    # Copy installer
    print(colored('Copying the installer', 'green'))
    cmds = ob.copy_file(installer, 'installer', node_details, conf_data, instance)
    logger.debug('Starting copying of installer')
    if parallel.upper() == 'TRUE':
        ob.execute_parallely(cmds)
    else:
        ob.execute_serially(cmds)

    # Extract installers
    print(colored('Extracting the installer', 'green'))
    cmds = ob.extract_tar(installer, 'installer', node_details, conf_data, instance)
    logger.debug('Starting extraction of installer')
    if parallel.upper() == 'TRUE':
        ob.execute_parallely(cmds)
    else:
        ob.execute_serially(cmds)

    file_for_pid = installation_path + '/scripts/pid.txt'
    pid = os.getpid()
    try:
        outfile = open(file_for_pid, 'w+')
    except PermissionError:
        print('Permission denied for ' + installation_path + '/scripts')
    outfile.write(str(pid))
    outfile.close()

    # Copy License
    print(colored('Copying the license file', 'green'))
    cmds = ob.copy_file(license, 'license', node_details, conf_data, instance)
    logger.debug('Starting copying of license')
    if parallel.upper() == 'TRUE':
        ob.execute_parallely(cmds)
    else:
        ob.execute_serially(cmds)

    # Extract License
    print(colored('Extracting the license', 'green'))
    cmds = ob.extract_tar(license, 'license', node_details, conf_data, instance)
    logger.debug('Starting extraction of license')
    if parallel.upper() == 'TRUE':
        ob.execute_parallely(cmds)
    else:
        ob.execute_serially(cmds)

    # Copy conf file
    if conf_file:
        print(colored('Copying appviewx.conf', 'green'))
        cmds = ob.copy_file(conf_file, 'conf', node_details, conf_data, instance)
        logger.debug('Starting copying of conf file')
        if parallel.upper() == 'TRUE':
            ob.execute_parallely(cmds)
        else:
            ob.execute_serially(cmds)

    if instance == 'singlenode' and change.lower() == 'yes':
        file = installation_path + '/conf/appviewx.conf'
        f = open(file, 'r+')
        conf_content = f.readlines()
        f.close()
        f = open(file, 'w+')
        for line in conf_content:
            if ':/home/appviewx/AppViewX' in line:
                line = line.replace(':/home/appviewx/AppViewX', ':' + installation_path)
            f.write(line)
        f.close()

    cmd_to_install = 'cd ' + installation_path + \
        '/scripts && ./appviewx --install'

    logger.debug('For further logs refer to scripts logs in <avx_dir>/logs/')

    logger.debug('Passing control to appviewx')
    logger.debug('running ./appviewx --install')
    try:
        subprocess.run(cmd_to_install, shell=True)
    except KeyboardInterrupt:
        sys.exit(1)

    logger.debug('Installation Completed')
