#!/usr/bin/python
# system_python_packages
import os
import platform
import socket
import time
import decimal
import resource
import socket
import sys
# Third_party_pacakges
import psutil
from termcolor import colored
import avx_commons
from config_parser import config_parser
current_file_path = os.path.dirname(os.path.realpath(__file__))
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
conf_file = current_file_path + "/../../conf/appviewx.conf"
conf_data = config_parser(conf_file)
import logger
lggr = logger.avx_logger('CONFIG_PARSER')

def print_format(
        first_value,
        second_value,
        key_color='white',
        value_color='green',
        third_color = 'green',
        third_value = '',
        value_check = False
    ):
        lggr.debug('%s \t %s \t %s' % (first_value,second_value,third_value)) 
        print_value = False
        if value_check:
           if second_value < third_value :
              print_value = True
              value_color = 'red'
        if print_value:
         print(
            '{0:7s} {1:35s} {2:7s} {3:40s} {4:20s} {5:20s}'.format(
                ' ', colored(
                    first_value, key_color), ':', colored(
                    second_value, value_color), colored(third_value,third_color),colored('(Not satisified)','yellow')))
        else:
         print(
            '{0:7s} {1:35s} {2:7s} {3:40s} {4:20s}'.format(
                ' ', colored(
                    first_value, key_color), ':', colored(
                    second_value, value_color), colored(third_value,third_color)))


class AVXPrerequisiteCheck(object):
    """Custom class for system requisite check
    """

    def __init__(self):
        pass

    @staticmethod
    def is_package_installed():
        """ is_package_installed to check whether the package is installed or not.

        @param
            package_name / type:string

        Return:
            string : True if it already installed
                   False if it is not installed

        Examples:
            is_package_installed('rsync')

       """
        try:
            not_installed_package = list()
            packages = [
                'nc',
                'nmap-ncat',
                'nmap',
                'curl',
                'sysstat',
                'lsof',
                'tcpdump',
                'rsync', 'openssl']
            nc_check = 0
            lggr.debug('Checking whether the packages is installed or not for the following packages : [%s]' % packages)
            lggr.info('Checking whether the packages is installed or not for the following packages : [%s]' % packages)
            not_installed_package = list()
            import subprocess
            for package in packages:
                cmd = 'rpm -ql ' + package
                k = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
                if 'not installed' in k:
                    if package == 'nc':
                        nc_check = 1
                    elif package == 'nmap-ncat':
                        if nc_check == 1:
                            not_installed_package.append(package)
                    else:
                        not_installed_package.append(package)
            if len(not_installed_package):
              lggr.debug('[%s] are not installed in localhost' % not_installed_package)
              lggr.error('[%s] are not installed in localhost' % not_installed_package)
              print_format(
                    "Package",
                    "Availability",
                    key_color='blue',
                    value_color='blue')
              for package in not_installed_package:
                print_format(package, 'not-installed', value_color='red')
              return False
            return True
        except Exception as e:
            lggr.error('Error in port checking: %s' % e)
            raise Exception(e)

    @staticmethod
    def system_details(ip=None):
        """is_package_installed to check whether the package is installed or not.

            @param
               ip_address / type:string

            Return:
                string : True if it executes succesfully
                       False if it execution failes

            Examples:
                system_details('192.168.50.20')

        """
        try:
            if ip is None:
                ip = socket.gethostbyname(socket.gethostname())
            lggr.debug('Checking system details in %s' % ip)
            lggr.info('Checking system details in %s' % ip)
            print_format("Host-ip", ip)
            print_format("Hostnames", socket.gethostname())
            print_format("Date", time.strftime("%H:%M:%Y"))
            print_format("Time", time.strftime("%d/%m/%y"))
            ram_details = psutil.virtual_memory()
            print_format(
                "Prerequisite",
                "Availability",
                key_color='blue',
                value_color='blue',
                third_color='blue',
                third_value='Recommended')
            print_format(
                "Operating system",
                platform.dist()[0] +
                platform.dist()[1],third_value='Redhat/Centos')
            print_format("Number of cpus", str(psutil.cpu_count()),third_value='8',value_check = True)
            print_format("Architecture", platform.architecture()[0],third_value='x86_64')
            ram_details = [str(round(decimal.Decimal(
                x / 1024 / 1024 / float(1024)), 0)) for x in ram_details]
            print_format("total ram memory", ram_details[0],third_value='16GB',value_check = True)
            print_format("free ram memory", ram_details[4],third_value='16GB',value_check = True)
            disk_details = psutil.disk_usage(os.path.expanduser('~'))
            disk_details = [str(round(decimal.Decimal(
                x / 1024 / 1024 / float(1024)), 1)) for x in disk_details]
            print_format("free disk space", disk_details[2],third_value ='200GB',value_check = True)
            print_format(
                "open files[ulimit -n]",
                str(resource.getrlimit(resource.RLIMIT_NOFILE)[1]),third_value='65535',value_check = True)
            print_format(
                "max processes[ulimit -u]",
                str(resource.getrlimit(resource.RLIMIT_NPROC)[1]),third_value='65535',value_check = True)
        except Exception as e:
            lggr.error('Error in port checking: %s' % e)
            raise Exception(e)
    
    @staticmethod
    def port_check(ip=None):
        """port_check used as main function to check the port status.

        Return:
            list : Return port_status
                'open','listening','not_reachable','not_available'

        Examples:
            port_check()

        """
        try:
            if ip is None:
                ip = socket.gethostbyname(socket.gethostname())

            components = ['mongodb', 'gateway', 'web']
            port_list = list()
            port_list.append(int(conf_data['COMMONS']['scheduler_port'][0]))
            lggr.debug('Port checking in %s' % ip)
            lggr.info('Port checking in %s' % ip)
            # if len(port_list):
            final_status = True
            print_format(
                "Port",
                "Status",
                key_color='blue',
                value_color='blue')
            for component in components:
                lggr.debug('Checking port status for component : %s' % component)
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
            lggr.debug('Port to be check for components in the local environment: %s' % port_list)
            for port in port_list:
                ip_port_status = avx_commons.port_status(ip, port)
                if ip_port_status == 'listening':
                    print_format(port, ip_port_status, value_color='red')
                    final_status = False
                else:
                    print_format(port, ip_port_status)
            components = conf_data['PLUGINS']['plugins']
            port_list = list()
            lggr.debug('Port to be check for plugin components in the local environment: %s' % port_list)
            for component in components:
                lggr.debug('Checking port status for component : %s' % component)
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
            static_ports = ['1812', '1813', '19164', '2195', '25', '389', '443', '4970', '4980', '4992', '4995', '636', '8102', '8105', '9514']
            port_list = port_list + static_ports
            lggr.debug('Final port check in the local environment : %s' % port_list)
            lggr.info('Final port check in the local environment : %s' % port_list)
            for port in port_list:
                ip_port_status = avx_commons.port_status(ip, port)
                if ip_port_status == 'listening':
                    print_format(port, ip_port_status, value_color='red')
                    final_status = False
                else:
                    print_format(port, ip_port_status)
            return final_status
        except Exception as e:
            lggr.error('Error in port checking: %s' % e)
            raise Exception(e)

if __name__ == '__main__':
    obj = AVXPrerequisiteCheck()

    try:
        obj.system_details()
        p_status = obj.port_check()
        packge_status = obj.is_package_installed()
    except Exception as e:
        lggr.error('Error in port checking: %s' % e)
        print(e)
