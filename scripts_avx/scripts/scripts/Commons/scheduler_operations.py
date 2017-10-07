"""Scheduler start/stop/restart/status."""

# The script is used to perform operations on the scheduler jar.
# The operations that can be performed are:
# 1. Start# 2. Stop
# 3. Status
# 4. Restart
import os
import sys
import socket
import logger
import using_fabric
import avx_commons
import signal
from monitorconfigure import synchronise
from initialize_common import InitializeCommon
import configparser
from avx_commons import get_username_path
from avx_commons import print_statement
from avx_commons import return_status_message_fabric
lggr = logger.avx_logger('scheduler_operation')
hostname = socket.gethostbyname(socket.gethostname())
current_file_path = os.path.dirname(os.path.realpath(__file__))
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def help_fun():
    """The function displays the help in case of wrong input."""
    print('Help function for scheduler jar')
    print('Options:')
    print('\t1. --start')
    print('\t2. --stop')
    print('\t3. --status')
    print('\t4. --restart')
    print('Usage:')
    print('\t./appviewx --start avx_platform_scheduler')
    print('\t./appviewx --restart avx_platform_scheduler')
    sys.exit(1)


class SchedulerOperations():
    """The class to perform scheduler operations."""

    def __init__(self, user_input, conf_data):
        """Define the class variables."""
        self.conf_data = conf_data
        self.user_input = user_input
        self.monitor_conf = os.path.abspath(
            current_file_path + '/../../conf/monitor.conf')
        self.config = configparser.ConfigParser()
        self.config.read(self.monitor_conf)
        try:
            self.scheduler_port = int(
                self.conf_data['COMMONS']['scheduler_port'][0])
        except:
            lggr.error('Scheduler port not found in conf file')

    def print_status(self, ip, status):
        """The function to print the according to input."""
        port = str(self.scheduler_port)
        if '--status' in self.user_input:
            version = 'v' + str(self.conf_data['COMMONS']['version'][0])
        else:
            version = ''

        print_statement('avx_platform_scheduler', version, ip, port, status)

    def add_remove_crontab_entry(self, operation):
        """Add/Remove crontab entries."""
        """The function is used to add remove crontab entries for
        avx-crontab.jar monitoring script entries from the
        scheduler monnitor template."""
        user, path = get_username_path(self.conf_data, hostname)
        file_to_remove = path + '/scripts/Commons/.one_time_config'
        try:
            os.remove(file_to_remove)
        except:
            lggr.debug('unable to delete: ' + file_to_remove)
        file = path + '/properties/mon_cron_file'
        scheduler_command = '*/3 * * * * APPVIEWX_SCRIPTS/../Python/bin/' +\
            'python APPVIEWX_SCRIPTS/Commons/scheduler_monitor.py '
        with open(file) as cron_file:
            file_content = cron_file.readlines()
        out_content = []
        for line in file_content:
            if 'scheduler_monitor' not in line:
                out_content.append(line)
        if operation.lower() == 'add':
            out_content.append(scheduler_command)
        with open(file, 'w+') as cron_file:
            cron_file.writelines(out_content)
        hosts = self.conf_data['MONGODB']['ips'] * 1
        if hostname in hosts:
            hosts.remove(hostname)
        for host in hosts:
            username, path = get_username_path(self.conf_data, host)
            cmd_to_delete_one_time_config_file = 'rm -rf ' + path +\
                '/scripts/Commons/.one_tim_config'
            cmd_to_add_content = 'echo ' + '\n'.join(out_content) + ' > ' +\
                path + '/properties/mon_cron_file '
            command = using_fabric.AppviewxShell([host], user=username)
            lggr.debug('Removing onetime config in  ' + host)
            command.run(cmd_to_delete_one_time_config_file)
            lggr.debug('editing mon_cron_file in ' + host)
            command.run(cmd_to_add_content)

    def operation(self):
        """Decide which function to call based upon the user input."""
        if len(self.user_input) > 2 and 'operation' not in self.user_input:
            help_fun()
        if 'operation' in self.user_input:
            self.user_input.remove('operation')
        operation = self.user_input[0].lower()
        self.operation = operation
        if operation == '--start':
            if not self.status():
                self.start()
        elif operation == '--stop':
            self.stop()
        elif operation == '--restart':
            self.restart()
        elif operation == '--status':
            ret = self.status(ret=False)
            if not ret:
                self.print_status('-', 'Not Running')
        else:
            help_fun()

    def start(self, add_entry=True):
        """The function to start avx-crontab jar."""
        from scheduler_monitor import SchedulerMonitor
        try:
            self.config.add_section('SCHEDULER')
        except:
            lggr.debug('SCHEDULER exists in monitor.conf')
        self.config.set('SCHEDULER', 'scheduler', 'true')
        with open(self.monitor_conf, 'w+') as conf_file:
            self.config.write(conf_file)
        synchronise()
        ip_started_on = SchedulerMonitor.initialize(SchedulerMonitor())
        if not ip_started_on:
            self.print_status('-', 'Not Started')
        else:
            self.print_status(ip_started_on, 'Starting')

        if add_entry:
            lggr.debug('Adding entry to crontab')
            self.add_remove_crontab_entry('add')
            lggr.debug('Initializing the crontab')
            InitializeCommon.crontab_configure(InitializeCommon())

    def stop(self, remove_entry=True):
        """The functio to stop avx-crontab jar."""
        from avx_commons import get_username_path
        _, path = get_username_path(self.conf_data, hostname)
        self.config.set('SCHEDULER', 'scheduler', 'false')
        with open(self.monitor_conf, 'w+') as conf_file:
            self.config.write(conf_file)
        synchronise()
        ip = self.status(ret=True)
        hosts = self.conf_data['MONGODB']['ips']
        primary_ip = self.conf_data['COMMONS']['scheduler_ip'][0]
        try:
            hosts.remove(primary_ip)
        except:
            print('Scheduler IP is not present in mongo hosts.')
            lggr.error('Scheduler IP is not present in mongo hosts.')
            sys.exit(1)
        hosts.insert(0, primary_ip)

        if ip:
            user, path = get_username_path(self.conf_data, ip)
            command = using_fabric.AppviewxShell([ip], user=user, pty=False)
            # status, res = return_status_message_fabric(f_obj)
            pid_command = 'lsof -t -i:' + str(self.scheduler_port)
            f_obj = command.run(pid_command)
            status, pid = return_status_message_fabric(f_obj)
            kill_cmd = 'kill -9 ' + pid
            f_obj = command.run(kill_cmd)
            status, res = return_status_message_fabric(f_obj)
            self.print_status(ip, 'Stopped')
        else:
            self.print_status('-', 'Not Running')

        if remove_entry:
            lggr.debug('Adding entry to crontab')
            self.add_remove_crontab_entry('remove')
            lggr.debug('Initializing the crontab')
            InitializeCommon.crontab_configure(InitializeCommon())

    def restart(self):
        """The function to restart avx-crontab jar."""
        lggr.debug(
            'Stopping avx-crontab.jar without deleting entry from crontab')
        self.stop(remove_entry=False)
        from time import sleep
        sleep(5)
        lggr.debug('Starting avx-crontab.jar without adding entry to crontab')
        self.start(add_entry=False)

    def status(self, ret=False):
        """The function to check status of avx-crontab jar."""
        from avx_commons import port_status
        ips = self.conf_data['MONGODB']['ips']
        for ip in ips:
            status = port_status(ip, self.scheduler_port)
            if status == 'listening':
                if not ret:
                    self.print_status(ip, 'Running')
                    return True
                else:
                    return ip
        return False
