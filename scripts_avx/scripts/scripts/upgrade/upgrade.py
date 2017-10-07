#!Python/bin/python
"""."""
import os
import sys
import socket
import subprocess
import glob
import readline
from termcolor import colored
import psutil
import logging
import math
import getpass
import signal
import configparser
from configobj import ConfigObj
from install import AppviewxShell

current_file_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostbyname(socket.gethostname())
logger = logging.getLogger('Upgrade')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('upgrade.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} ' +
    '%(levelname)s\t%(message)s',
    '%m-%d %H:%M:%S')
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
to_exit = False
main_thread = []


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


class UpgradeAVX():
    """The class to upgrade AppViewX from older version to current version."""

    def __init__(self):
        """Define the class variables."""
        self.hostname = socket.gethostbyname(socket.gethostname())

    def get_files(self):
        """."""
        self.patch_file = os.path.abspath(sys.argv[1])
        try:
            self.license_file = glob.glob(
                ''.join(map(either, '*license.tar.gz')))[0]
        except Exception:
            while True:
                self.license_file = os.path.abspath(input(
                    'Enter the path of the license file: '))
                if not self.license_file.lower().endswith('license.tar.gz') \
                        or not os.path.isfile(self.license_file):
                    print('License file should be in *license.tar.gz format!')
                elif self.license_file.startswith(
                        self.appviewx_installed_location + '/'):
                    print(
                        'License file cannot be present inside the AppViewX' +
                        ' installed directory!')
                else:
                    break
        logger.info('Patch file: ' + self.patch_file)
        logger.info('License file: ' + self.license_file)

    def get_old_installation_location(self):
        """."""
        while True:
            self.appviewx_installed_location = os.path.abspath(input(
                'Enter the path where AppViewX is installed: '))
            if not os.path.exists(self.appviewx_installed_location +
                                  '/db/mongodb/data'):
                print('Data folder not found at: ' +
                      self.appviewx_installed_location + '/db/mongodb/data')
                print(
                    'Please input a valid loation where AppViewX is installed')
            else:
                break
        logger.info(
            'Old installation path: ' + self.appviewx_installed_location)
        self.old_conf_file = self.appviewx_installed_location +\
            '/conf/appviewx.conf'
        self.old_conf_data = ConfigObj(self.old_conf_file)
        try:
            self.version = self.old_conf_data[
                'VERSION_NUMBER'].lstrip('v').lstrip('V')
        except:
            self.version = self.old_conf_data[
                'VERSION'].lstrip('v').lstrip('V')
        logger.info('Old installed version: v' + self.version)

    def validate_meta_and_old_conf_file(self, template_file_source):
        """Function to validate plugins.meta."""
        meta_file = template_file_source
        try:
            # import collections
            meta_obj = configparser.ConfigParser()
            meta_obj.read(meta_file)
            try:
                meta_obj['PLUGINS']
            except KeyError:
                print(
                    colored(
                        'PLUGINS section not found in plugins.meta', 'red'))
                sys.exit(1)
            try:
                meta_obj['LOGSTASH']
            except KeyError:
                print(
                    colored(
                        'LOGSTASH section not found in plugins.meta', 'red'))
                sys.exit(1)
        except configparser.Error as e:
            print(colored(e, 'red'))
            sys.exit(1)
        if len(self.hosts) > 1:
            self.validate_datacenter_details()

    def validate_datacenter_details(self):
        """Functio to validate datacenter details in old conf file."""
        old_conf_file = os.path.abspath(
            self.appviewx_installed_location + '/conf/appviewx.conf')
        with open(old_conf_file) as conf_file:
            old_conf_content = conf_file.readlines()
        datacenter_str = None
        for line in old_conf_content:
            if line.lower().startswith('datacenter'):
                datacenter_str = line.split('=')[-1]
                break
        if not datacenter_str:
            print(
                'Unable to find datacenter related entries' +
                ' in old appviewx.conf')
            logger.error(
                'Unable to find datacenter related entries' +
                ' in old appviewx.conf')
            print('Exiting!')
            sys.exit(1)
        all_ips = []
        for center_ips in datacenter_str.split():
            center, ips = center_ips.split(':')
            for ip in ips.split(','):
                all_ips.append(ip)
        all_ips = list(set(all_ips))
        missing_ips = []
        for ip in self.hosts:
            if ip not in all_ips:
                missing_ips.append(ip)
        if len(missing_ips):
            print(
                'Following nodes do not have datacenter ' +
                'entries in appviewx.conf: ')
            print(', '.join(missing_ips))
            sys.exit(1)

    @staticmethod
    def print_format(first_value, second_value, key_color='white',
                     value_color='green', third_color='green', third_value=''):
        """."""
        try:
            global prereq_str
            prereq_str +=\
                '\n' + '{0:7s} {1:35s} {2:7s} {3:40s} {4:20s}'.format(
                    ' ', colored(first_value, key_color), ':',
                    colored(second_value, value_color), colored(
                        third_value, third_color))
        except KeyboardInterrupt:
            sys.exit(1)

    def prerequisite(self, conf_data):
        """."""
        try:
            global prereq_str
            global warn_str
            global to_exit
            for ip, user, path in zip(self.hosts, self.usernames, self.paths):
                conn_port = 22
                Bcolors.OKBLUE
                fab_ob = AppviewxShell([ip], user=user, port=conn_port)
                cmd = ''
                host_ip_add, status = fab_ob.run(
                    cmd + "hostname -i 2> /dev/null")
                prereq_str += '\n' + "\thost-ip\t\t\t   :   \t" +\
                    str(host_ip_add.strip())
                host_name_info, status = fab_ob.run(
                    cmd + "hostname 2> /dev/null")
                prereq_str += '\n' + "\thostname\t\t   :   \t" +\
                    host_name_info.strip()
                system_date_info, status = fab_ob.run(
                    cmd + "date +%Y/%m/%d 2> /dev/null")
                date_val = system_date_info.strip()
                date_check[ip] = date_val
                prereq_str += '\n' + "\tdate\t\t\t   :   \t" + date_val
                system_time_info, status = fab_ob.run(
                    cmd + "date +%H:%M:%S 2> /dev/null")
                time_val = system_time_info.strip()
                time_check[ip] = time_val
                prereq_str += '\n' + "\ttime\t\t\t   :   \t" + time_val
                system_zone_time_info, status = fab_ob.run(
                    cmd + "date +%Z 2> /dev/null")
                zone_time_val = system_zone_time_info.strip()
                zone_time_check[ip] = zone_time_val
                UTC_list[ip], status = fab_ob.run(cmd + 'date -u 2> /dev/null')
                Bcolors.ENDC
                prereq_str += '\n' + colored(
                    "\tPrerequisite\t\t   :   \tRecommended\t\t   :" +
                    "   \tAvailablity", 'blue')
                warn_str += colored(
                    "\tPrerequisite\t\t   :   \tRecommended\t\t   :" +
                    "   \tAvailablity", 'blue')
                operating_system_str, status = fab_ob.run(
                    cmd + " python -mplatform 2>/dev/null")
                operating_system = operating_system_str.split('-')[-3]
                os_version = operating_system = operating_system_str.split(
                    '-')[-2]
                prereq_str += '\n' + "\toperating system\t   :" +\
                    "   \tRedHat/CentOs\t\t   :   \t" + (operating_system)
                no_of_cpu = psutil.cpu_count()
                if no_of_cpu < 8:
                    no_of_cpu = Bcolors.FAIL + str(no_of_cpu) + Bcolors.ENDC
                    warn_str += '\n' + "\tnumber of cpus\t\t   :" + \
                        "   \t8\t\t\t   :   \t" + str(no_of_cpu)
                prereq_str += '\n' + "\tnumber of cpus\t\t   :" +\
                    "   \t8\t\t\t   :   \t" + str(no_of_cpu)
                architecture, status = fab_ob.run(
                    cmd + "lscpu 2> /dev/null | grep Architecture |" +
                    " awk '{print $2}'")
                if 'x86_64' not in architecture:
                    architecture = Bcolors.FAIL + architecture + Bcolors.ENDC
                    warn_str += '\n' + "\tarchitecture\t\t   :" +\
                        "   \tx86_64\t\t\t   :   \t" + str(architecture)
                prereq_str += '\n' + "\tarchitecture\t\t   :" +\
                    "   \tx86_64\t\t\t   :   \t" + str(architecture)
                total_memory, status = fab_ob.run(
                    cmd + " free -m 2> /dev/null | grep \"Mem\" |" +
                    "awk '{ print($2/1024) }' ")
                total_memory = int(math.ceil(float(total_memory.strip())))
                if total_memory < 16:
                    total_memory = Bcolors.FAIL + str(
                        total_memory) + Bcolors.ENDC
                    warn_str += '\n' + "\ttotal ram memory\t   :" +\
                        "   \t16GB\t\t\t   :   \t" + str(total_memory)
                prereq_str += '\n' + "\ttotal ram memory\t   :" + \
                    "   \t16GB\t\t\t   :   \t" + str(total_memory)
                free_memory, status = fab_ob.run(
                    cmd + " free -m 2> /dev/null | grep \"Mem\" |" +
                    " awk '{ printf($4/1024)}' ")
                free_memory = int(math.ceil(float(free_memory.strip())))
                if free_memory < 16:
                    free_memory = Bcolors.FAIL + str(
                        free_memory) + Bcolors.ENDC
                prereq_str += '\n' + "\tfree ram memory\t\t   :" + \
                    "   \t16GB\t\t\t   :   \t" + str(free_memory)
                free_disk_space, status = fab_ob.run(
                    cmd + "df -Ph . 2> /dev/null | tail -1 | awk '{print $4}'")
                free_disk_space = int(float(
                    free_disk_space.strip().strip('G').strip('M')))
                if free_disk_space < 200:
                    free_disk_space = Bcolors.FAIL + str(
                        free_disk_space) + Bcolors.ENDC
                    warn_str += '\n' +\
                        "\tfree disk space\t\t   :   \t200GB\t\t\t   :   \t" +\
                        str(free_disk_space)
                prereq_str += '\n' +\
                    "\tfree disk space\t\t   :   \t200GB\t\t\t   :   \t" +\
                    str(free_disk_space)
                ulimit_value_file, status = fab_ob.run(
                    cmd + "ulimit -n 2> /dev/null")
                ulimit_value_file = int(ulimit_value_file.strip())
                if ulimit_value_file < 65535:
                    ulimit_value_file = Bcolors.FAIL + str(
                        ulimit_value_file) + Bcolors.ENDC
                    warn_str += '\n' + "\topen files[ulimit -n]\t   :" + \
                        "   \t65535\t\t\t   :   \t" + str(ulimit_value_file)
                prereq_str += '\n' + "\topen files[ulimit -n]\t   : " + \
                    "  \t65535\t\t\t   :   \t" + str(ulimit_value_file)
                ulimit_value_process, status = fab_ob.run(
                    cmd + "ulimit -u 2> /dev/null")
                ulimit_value_process = int(ulimit_value_process.strip())
                if ulimit_value_process < 65535:
                    ulimit_value_process = Bcolors.FAIL + str(
                        ulimit_value_process) + Bcolors.FAIL
                    warn_str += '\n' + "\tmax processes[ulimit -u]   :" + \
                        "   \t65535\t\t\t   :   \t" + str(ulimit_value_process)
                prereq_str += '\n' + "\tmax processes[ulimit -u]   :" + \
                    "   \t65535\t\t\t   :   \t" + str(ulimit_value_process)
                prereq_str += ''
                self.print_format(
                    'Packages',
                    'Availability',
                    key_color='blue',
                    value_color='blue')
                packages = ['nc',
                            'nmap-ncat',
                            'nmap',
                            'curl',
                            'sysstat',
                            'tcpdump',
                            'rsync',
                            'lsof',
                            'openssl']
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
                self.port_check(conf_data, ip)
            if to_exit:
                sys.exit(1)
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
        global warn_str
        global to_exit
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
            if len(prerequisite_status_check) or len(prerequisite_port_check):
                print(prereq_str)
                print(colored(
                    'Either a package is not installed or port is listening',
                    'red'))
                logger.debug('Prerequisite check failed!')
                to_exit = True
            elif len(warn_str) > 125:
                print(colored(
                    'The following system specifications are not upto mark ' +
                    'for ' + ip + '.', 'yellow'))
                print(warn_str)
            else:
                print(
                    '{0:30s}  {1:15s}  {2:10s} {3:5s}'.format(
                        ' ', ip, '', colored('Success', 'green')))
                logger.debug('Prerequisite check successfull.')
            prereq_str = ''
            warn_str = ''
            return final_status
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            raise Exception(e)

    def copy_files_to_patch_directory(self):
        """Function to copy license file and patch file to all nodes."""
        if len(list(set(self.usernames))) == len(list(set(self.paths))) == 1:
            fab_obj = AppviewxShell(
                self.hosts, user=self.usernames[0], parallel=True)
            for file in [self.patch_file, self.license_file]:
                if 'license' in file.lower():
                    file_type = 'License'
                else:
                    file_type = 'Patch'
                if file_type == 'License':
                    print('Copying ' + file_type + ' file to   : ' + ', '.join(
                        self.hosts))
                print(
                    'Copying ' + file_type + ' file to : ' + ', '.join(
                        self.hosts))
                logger.info('Copying ' + file.split('/')[-1] +
                            ' to ' + self.usernames[0] + '@' +
                            ', '.join(self.hosts) + ' :' + self.paths[0] +
                            '/patch/' + file.split('/')[-1])
                fab_obj.file_send(
                    file, self.paths[0] + '/patch/' + file.split('/')[-1])
            del fab_obj
        else:
            for file in [self.patch_file, self.license_file]:
                if 'license' in file.lower():
                    file_type = 'License'
                else:
                    file_type = 'Patch'
                for ip, user, path in zip(
                        self.hosts, self.usernames, self.paths):
                    logger.info('Copying ' + file.split('/')[-1] +
                                ' to ' + user + '@' + ip + ':' + path +
                                '/patch/' + file.split('/')[-1])
                    fab_obj = AppviewxShell([ip], user=user)
                    print(
                        'Copying ' + file_type + ' file to: ' + ip)
                    fab_obj.file_send(
                        file, path + '/patch/' + file.split('/')[-1])
                    del fab_obj

    def extract_patch(self):
        """."""
        if len(list(set(self.usernames))) == len(list(set(self.paths))) == 1:
            fab_obj = AppviewxShell(
                self.hosts, user=self.usernames[0], parallel=True)
            cmd_to_create_temp_folder = 'mkdir -p ' + self.paths[0] +\
                '/patch/AppPatch'
            cmd_to_extract_patch_file = 'cd ' + self.paths[0] + \
                '/patch && tar -xf ' +\
                self.patch_file.split('/')[-1] + ' -C AppPatch'
            complete_cmd = cmd_to_create_temp_folder +\
                ' ; ' + cmd_to_extract_patch_file
            print('Extracting Patch file on: ' + ', '.join(self.hosts))
            logger.debug(
                'Creating AppPatch directory inside the patch folder for: ' +
                ', '.join(self.hosts))
            fab_obj.run(complete_cmd)
            del fab_obj
        else:
            for ip, user, path in zip(self.hosts, self.usernames, self.paths):
                fab_obj = AppviewxShell([ip], user=user)
                cmd_to_create_temp_folder = 'mkdir -p ' + path +\
                    '/patch/AppPatch'
                cmd_to_extract_patch_file = 'cd ' + path +\
                    '/patch && tar -xf ' +\
                    self.patch_file.split('/')[-1] + ' -C AppPatch'
                complete_cmd = cmd_to_create_temp_folder +\
                    ' ; ' + cmd_to_extract_patch_file
                logger.debug(
                    'Creating AppPatch directory' +
                    ' inside the patch folder for: ' +
                    ip)
                print('Extracting Patch file on: ' + ip)
                fab_obj.run(complete_cmd)
                del fab_obj

    def copy_files_out_of_patch_directory(self):
        """."""
        for ip, user, path in zip(self.hosts, self.usernames, self.paths):
            fab_obj = AppviewxShell([ip], user=user)
            cmd_to_copy = 'cd ' + path +\
                '/patch/AppPatch ; rm -rf patch ; ' +\
                'rsync -avz * ' + path + '/'
            logger.debug(cmd_to_copy)
            cmd_to_copy_license = 'cp ' + path + '/patch/' +\
                self.license_file.split('/')[-1] + ' ' + path +\
                '/avxgw/' +\
                ' ; cd ' + path + '/avxgw && tar -xf ' +\
                self.license_file.split('/')[-1]
            logger.debug(cmd_to_copy_license)
            complete_cmd = cmd_to_copy + ' ; ' + cmd_to_copy_license
            print('Applying Patch on: ' + ip)
            fab_obj.run(complete_cmd)
            del fab_obj

    def old_conf_data_parser(self):
        """."""
        multinode = self.old_conf_data['APPVIEWX_SSH'].lower()
        if multinode == 'false':
            self.hosts = [self.hostname]
            self.usernames = [getpass.getuser()]
            self.paths = [self.appviewx_installed_location]
        else:
            self.hosts = []
            self.usernames = []
            self.paths = []
            old_hosts = self.old_conf_data['APPVIEWX_SSH_HOSTS']
            for host in old_hosts:
                ip, path = host.split(':')
                self.hosts.append(ip)
                self.paths.append(path)
            if 'str' in str(type(self.old_conf_data['APPVIEWX_SSH_USERNAME'])):
                self.usernames = [
                    self.old_conf_data[
                        'APPVIEWX_SSH_USERNAME']] * len(self.hosts)
            else:
                self.usernames = self.old_conf_data['APPVIEWX_SSH_USERNAME']

    def new_conf_data_parser(self):
        """."""
        from config_parser import config_parser
        self.old_conf_data = config_parser(self.old_conf_file)
        self.hosts = self.old_conf_data['ips']
        self.usernames = self.old_conf_data['usernames']
        self.paths = self.old_conf_data['paths']

    def stop_all(self):
        """."""
        if self.version < '12.0.0':
            cmd_to_stop_components = \
                'cd ' + self.appviewx_installed_location +\
                '/scripts && ./appviewx.py --stop all'
        else:
            cmd_to_stop_components = \
                'cd ' + self.appviewx_installed_location +\
                '/scripts && ./appviewx --stop all'

        logger.info('Stopping the old components.')
        logger.debug(cmd_to_stop_components)
        subprocess.run(cmd_to_stop_components, shell=True)

    def call_conf_merge(self, backup=True):
        """."""
        to_exit = False
        for ip, user, path in zip(self.hosts, self.usernames, self.paths):
            fab_obj = AppviewxShell([ip], user=user)
            if backup:
                cmd_for_conf_backup = 'cd ' + path + '/conf && ' +\
                    'mv appviewx.conf appviewx_backup.conf'
                logger.info('Taking backup of old appviewx.conf on: ' + ip)
                fab_obj.run(cmd_for_conf_backup)
                cmd_for_log_prop_scripts_backup = 'cd ' + path +\
                    ' && tar -zcvf old_scripts_logs_properties.tar.gz ' +\
                    'scripts logs properties;' +\
                    ' rm -rf scripts logs jre properties Python ' +\
                    'web jdk service iAgent*'
                logger.info(
                    'Taking backup of scripts, properties and logs on: ' + ip)
                fab_obj.run(cmd_for_log_prop_scripts_backup)
            else:
                cmd_for_conf_merge = path + '/Python/bin/python ' + path +\
                    '/scripts/upgrade/conf_merge.py'
                logger.info('Performing conf merge operation on: ' + ip)
                res, status = fab_obj.run(cmd_for_conf_merge)
                if not status:
                    print('Unable to do conf-merge on: ' + ip)
                    logger.error(res)
                    to_exit = True
        if to_exit:
            sys.exit(1)

    def upgrade(self):
        """."""
        from config_parser import config_parser
        self.get_old_installation_location()
        self.get_files()
        template_file_source = os.path.abspath(
            current_file_path + '/plugins.meta')
        if not os.path.exists(template_file_source):
            print(colored('plugins.meta file not found!!', 'red'))
            sys.exit(1)
        template_file_dest = os.path.abspath(
            self.appviewx_installed_location + '/conf/plugins.meta')
        if self.version < '12.0.0':
            self.old_conf_data_parser()
        else:
            self.new_conf_data_parser()
        current_conf = config_parser('appviewx.conf')
        logger.debug('Host details for the existing setup: ')
        logger.debug('hosts: [ ' + ', '.join(self.hosts) + ' ]')
        logger.debug('usernames: [ ' + ', '.join(self.usernames) + ' ]')
        logger.debug('paths: [ ' + ', '.join(self.paths) + ' ]')

        for ip, user, path in zip(self.hosts, self.usernames, self.paths):
            fab_ob = AppviewxShell([ip], user=user)
            template_file_dest = path + '/conf/plugins.meta'
            fab_ob.file_send(template_file_source, template_file_dest)

        self.validate_meta_and_old_conf_file(template_file_source)

        self.stop_all()

        print('Starting Prerequisite Check')
        self.prerequisite(current_conf)
        self.call_conf_merge(backup=True)

        self.copy_files_to_patch_directory()
        self.extract_patch()
        self.copy_files_out_of_patch_directory()

        file_for_pid = self.appviewx_installed_location + '/scripts/pid.txt'
        pid = os.getpid()
        try:
            outfile = open(file_for_pid, 'w+')
            outfile.write(str(pid))
            outfile.close()
        except IOError:
            logger.error('Unable to open pid.txt')

        self.call_conf_merge(backup=False)
        cmd = 'cd ' + self.appviewx_installed_location +\
            '/scripts && ./appviewx --upgrade ' +\
            str(self.version)
        subprocess.run(cmd, shell=True)


ob = UpgradeAVX()
ob.upgrade()
