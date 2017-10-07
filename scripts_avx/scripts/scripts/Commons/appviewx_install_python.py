"""The script to install AppViewX."""
import os
import sys
import psutil
import signal
import socket
import logger
import traceback
import subprocess
import avx_commons
import time
from termcolor import colored
import avx_cert_gen
import using_fabric
from config_parser import config_parser
import set_path
avx_path = set_path.AVXComponentPathSetting()
lggr = logger.avx_logger('install_appviewx_')
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))
if not os.path.realpath('Mongodb/') in sys.path:
    sys.path.append(current_file_path + '/../Mongodb/')
if not os.path.realpath('Web/') in sys.path:
    sys.path.append(current_file_path + '/../Web/')
if not os.path.realpath('Gateway/') in sys.path:
    sys.path.append(current_file_path + '/../Gateway/')
if not os.path.realpath('Plugins/') in sys.path:
    sys.path.append(current_file_path + '/../Plugins/')
if not os.path.realpath('Logstash/') in sys.path:
    sys.path.append(current_file_path + '/../Logstash/')

signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class AppViewXInstall():
    """Install AppViewX."""

    """The class that handles the installation of AppViewX
    for both singlenode and multinode setup.
    The class calls the following modules to instal AppViewX:
    1. Prerequisite check
    2. Initialization
    3. dbstart
    4. dbimport and jarmigration
    5. start individual components"""

    def __init__(self):
        """The class to define all the class variables."""
        try:
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.python_path = '/Python/bin/python'
            self.script_path = '/scripts'
            self.to_exit = 0
            self.print_data = 0
        except IOError:
            print(colored('appviewx.conf not found!', 'red'))
            lggr.error('appviewx.conf not found')
            sys.exit(1)
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    @staticmethod
    def execute_command(cmd):
        """Execute the commands."""
        """The method is used to execute the command and
        return the subprocess object"""
        try:
            cmd = cmd.strip()
            if cmd.startswith('"'):
                cmd = cmd.strip('"')
            ps = subprocess.run(cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if ps.returncode:
                lggr.error('Error in executing command: ' + cmd)
                lggr.error(ps.stdout.decode())
            return ps
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    def extract_logstash(self):
        """Function to extract logstash."""
        from avx_commons import get_username_path
        from avx_commons import return_status_message_fabric
        if 'LOGSTASH' in self.conf_data.keys():
            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = get_username_path(self.conf_data, ip)
                cmd = 'cd ' + path + ' && tar -xf logstash.tar.gz'
                fab_ob = using_fabric.AppviewxShell([ip], user=user)
                px = fab_ob.run(cmd)
                stat, res = return_status_message_fabric(px)
                if stat:
                    lggr.debug('Extracted logstash.tar.gz on: ' + ip)
                else:
                    lggr.error('Unable to extract logstash.tar.gz on: ' + ip)
                    lggr.debug('Unable to extract logstash.tar.gz on: ' + ip)
        else:
            lggr.debug('No logstash entry in appviewx.conf')

    def remove_role_template(self):
        """Execute the role template jar."""
        java_path = os.path.abspath(
            avx_path.appviewx_path + '/jre/bin/java')
        properties_path = os.path.abspath(
            avx_path.appviewx_path + '/properties/')
        acf_admin_jar_path = os.path.abspath(
            avx_path.appviewx_path + '/avxgw/acf-admin-1.0.0.jar')
        cmd_to_execute = java_path + ' -Davx_logs_home=' + current_file_path +\
            '/../../logs/acf-admin.logs -cp ' + acf_admin_jar_path +\
            ':' + avx_path.appviewx_path +\
            '/Plugins/framework/framework-db.jar:' +\
            properties_path + ' -Dlog4j.configuration=file:' +\
            avx_path.appviewx_path +\
            '/properties/log4j.acf-admin com.appviewx.acfadmin.main.AcfAdminMain'
        if not os.path.isfile(avx_path.appviewx_path + '/Plugins/framework/framework-db.jar'):
            lggr.error('framework-db.jar is missing in %s directory ' % avx_path.appviewx_path + '/Plugins/framework')
            lggr.error('cmd to execute acf-admin jar: %s' % cmd_to_execute)
            print (colored('framework-db.jar is missing in %s directory ' % avx_path.appviewx_path + '/Plugins/framework.So acf-admin.jar is not executing', 'red'))
            return
        cmd_to_execute = java_path + ' -Davx_logs_home=' + current_file_path + '/../../logs/acf-admin.logs -cp ' + acf_admin_jar_path + ':' + avx_path.appviewx_path + '/Plugins/framework/framework-db.jar:' + properties_path + ' com.appviewx.acfadmin.main.AcfAdminMain'
        ps = self.execute_command(cmd_to_execute)
        result = ps.stdout.decode()
        if 'error' in result.lower():
            print (colored('Error in executing (acf-admin.jar): %s' % cmd_to_execute, 'red'))
            print (result)
            lggr.error('acf-admin.jar not executed successfully')
            lggr.error('Error in executing : %s' % cmd_to_execute)
            lggr.error('Error : ' + ps.stderr.decode())

    def update_scheduler_port(self, conf_data, primary_ip):
        """Method to update scheduler jar port in conf_file."""
        ips = conf_data['ENVIRONMENT']['ips']
        for node in conf_data['ENVIRONMENT']['ssh_hosts']:
            node, path = node.split(':')
            index = ips.index(node.split('@')[1])
            ip = node.split('@')[1]
            conn_port = conf_data['ENVIRONMENT']['ssh_port'][index]
            ip = node.split('@')[1]
            if ip == self.hostname:
                cmd = ''
            else:
                cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' +\
                    str(conn_port) + ' ' + node
            cmd = cmd + ' sed -i "s/SCHEDULER_IP.*/SCHEDULER_IP=' +\
                primary_ip + '/g" ' + path + '/conf/appviewx.conf'
            self.execute_command(cmd)

    def license_and_data_folder_check(self):
        """Perform the prerequisite check on all the nodes."""
        try:
            # Check license present on all gateway nodes
            # Check data folder present on all DB hosts.
            license_files = ['/avxgw/avxgw',
                             '/avxgw/acf-admin-1.0.0.jar',
                             '/avxgw/Gateway_key.txt']
            data_path = '/db/mongodb/data/db'
            for ip in self.conf_data['GATEWAY']['ips']:
                user, path = avx_commons.get_username_path(self.conf_data, ip)
                index = self.conf_data['ENVIRONMENT']['ips'].index(ip)
                conn_port = str(
                    self.conf_data['ENVIRONMENT']['ssh_port'][index])
                lggr.debug('Checking for license files on ' + ip)
                for file in license_files:
                    if ip == self.hostname:
                        cmd = ''
                    else:
                        cmd = 'ssh -oStrictHostKeyChecking=no -p ' +\
                            conn_port + ' ' + user + '@' + ip
                    cmd = cmd + ' "ls -l ' + path + file + ' | wc -l"'
                    ps = self.execute_command(cmd)
                    if ps.stderr:
                        lggr.error('License file(s) not found on ' + ip)
                        print('License file(s) not found on ' + ip)
                        self.to_exit = 1
                        break
            for ip in self.conf_data['MONGODB']['ips']:
                user, path = avx_commons.get_username_path(self.conf_data, ip)
                index = self.conf_data['ENVIRONMENT']['ips'].index(ip)
                conn_port = str(
                    self.conf_data['ENVIRONMENT']['ssh_port'][index])
                if ip == self.hostname:
                    cmd = ''
                else:
                    cmd = 'ssh -oStrictHostKeyChecking=no -p ' +\
                        conn_port + ' ' + user + '@' + ip
                lggr.debug('Checking for data folder on ' + ip)
                cmd = cmd + ' "ls -l ' + path + data_path + ' | wc -l"'
                ps = self.execute_command(cmd)
                if not ps.stderr:
                    print('Data folder present on ' + ip)
                    lggr.error('Data folder present on ' + ip)
                    self.print_data = 1
                    self.to_exit = 1
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)
        finally:
            if self.print_data:
                print('Delete the data folder to proceed.')
            if self.to_exit:
                sys.exit(1)

    def prerequisite(self):
        """Start the MongoDB."""
        try:
            from mongodb_setup import print_success
            import using_fabric
            pid_list = psutil.pids()
            try:
                pid = int(open('pid.txt').read().strip())
                os.remove('pid.txt')
            except:
                pid = -1
            if pid in pid_list:
                lggr.debug('Not performing prerequisite check again.')
                return
            self.to_exit = 0
            print('Starting prerequisite check\n')
            for ip in self.conf_data['ENVIRONMENT']['ips']:
                user, path = avx_commons.get_username_path(self.conf_data, ip)
                cmd_to_check_prerequisite = path + self.python_path +\
                    ' ' + path + self.script_path +\
                    '/Commons/prerequisite.py'
                if ip == self.hostname:
                    ps = self.execute_command(cmd_to_check_prerequisite)
                    res = ps.stdout.decode()
                    if 'listening' in res or 'not-installed' in res:
                        self.to_exit = 1
                        print(ps.stdout.decode())
                        lggr.debug('Prerequisite check failed on ' + ip)
                    else:
                        print_success(ip, colored('Success', 'green'))
                        lggr.debug('Prerequisite check successful on ' + ip)
                else:
                    command = using_fabric.AppviewxShell([ip], user=user)
                    lggr.debug(cmd_to_check_prerequisite)
                    l = command.run(cmd_to_check_prerequisite)
                    key, value = l
                    status = list(value)[-1][-1]
                    res = list(value)[-1][0]
                    if not status:
                        lggr.error('Error in checking prerequisite on: ' + ip)
                        print_success(ip, 'Error')
                        continue
                    if 'listening' in res or 'not-installed' in res:
                        self.to_exit = 1
                        print(res)
                        lggr.debug('Prerequisite check failed on ' + ip)
                    else:
                        print_success(ip, colored('Success', 'green'))
                        lggr.debug('Prerequisite check successful on ' + ip)
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)
        finally:
            if self.to_exit:
                print('Either package not installed or port listening')
                sys.exit(1)

    def initialization(self):
        """Start the MongoDB."""
        try:
            from initialize_common import InitializeCommon
            from initialize_mongodb import InitializeMongoDB
            from initialize_gateway import InitializeGateway
            from initialize_web import InitializeWeb
            from initialize_plugins import InitializePlugins
            from initialize_logstash import Initializelogstash
            from mongodb_setup import print_success
            lggr.debug("Starting the Commons Initialization")
            lggr.info("Starting the Commons Initialization")
            InitializeCommon.initialize(InitializeCommon())
            lggr.debug("Commons Initialized")
            lggr.info("Commons Initialized")
            print_success('Core Components', 'Initialized')
            lggr.debug("Starting the Mongodb Initialization")
            lggr.info("Starting the Mongodb Initialization")
            InitializeMongoDB.initialize(InitializeMongoDB())
            print_success('avx_platform_database', 'Initialized')
            lggr.debug("Database Initialized")
            lggr.info("Database Initialized")
            lggr.debug("Starting the Plugins Initialization")
            lggr.info("Starting the Plugins Initialization")
            InitializePlugins.initialize(InitializePlugins())
            print_success('avx_subsystems', 'Initialized')
            lggr.debug("Plugins Initialized")
            lggr.info("Plugins Initialized")
            lggr.debug("Starting the Gateway Initialization")
            lggr.info("Starting the Gateway Initialization")
            InitializeGateway.initialize(InitializeGateway())
            lggr.debug("Gateway Initialized")
            lggr.info("Gateway Initialized")
            print_success('avx_platform_gateway', 'Initialized')
            lggr.debug("Starting the Logstash initialization")
            lggr.info("Starting the Logstash initialization")
            Initializelogstash.initialize(Initializelogstash())
            print_success('avx_platform_logs', 'Initialized')
            lggr.debug("Starting the Web Initialization")
            lggr.info("Starting the Web Initialization")
            InitializeWeb.initialize(InitializeWeb())
            print_success('avx_platform_web', 'Initialized')
            lggr.debug("Web Initialized")
            lggr.info("Web Initialized")
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    def dbstart(self):
        """Start the MongoDB."""
        try:
            cmd_to_dbstart = current_file_path + '/../../' +\
                self.python_path + ' ' + current_file_path +\
                '/appviewx_dbstart_python.py'
            ps = subprocess.run(cmd_to_dbstart, shell=True)
            if ps.stderr:
                print(colored('Error in starting MongoDB', 'red'))
                lggr.debug('Error in starting MongoDB')
                lggr.error(ps.stderr.decode())
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    def dbimport_and_jarmigration(self):
        """Perform dbimport and jarmigration operation."""
        try:
            python_path = os.path.abspath(
                current_file_path + '/../../Python/bin/python ')
            script_path = os.path.abspath(
                current_file_path + '/../Mongodb/mongodb_setup.py')
            mongodb_setup_cmd = python_path + script_path + ' '
            gridfs_cmd = mongodb_setup_cmd + '--dbimport gridfs'
            master_script_cmd = mongodb_setup_cmd + '--dbimport Master_Scripts'
            fresh_scripts_cmd = mongodb_setup_cmd + '--dbimport fresh'
            jar_migration_scripts = mongodb_setup_cmd + '--jarmigration fresh'
            print('Starting DatabaseImport')
            lggr.debug('Starting DatabaseImport')
            lggr.debug('Executing Gridfs scripts')
            ps = self.execute_command(gridfs_cmd)
            if ps.returncode:
                lggr.error('Error in executing Gridfs scripts')
            else:
                lggr.debug('Gridfs scripts executed')
            lggr.debug('Executing Master scripts')
            ps = self.execute_command(master_script_cmd)
            if ps.returncode:
                lggr.error('Error in executing Master scripts')
            else:
                lggr.debug('Master scripts executed')
            lggr.debug('Executing Fresh scripts')
            ps = self.execute_command(fresh_scripts_cmd)
            if ps.returncode:
                lggr.error('Error in executing Fresh scripts')
            else:
                lggr.debug('Fresh scripts executed')
            print('Database import completed')
            print('Starting databaseMigration')
            lggr.debug('Executing Jarmigration scripts')
            ps = self.execute_command(jar_migration_scripts)
            if ps.returncode:
                lggr.error('Error in executing Jarmigration scripts')
            else:
                lggr.debug('Jarmigration scripts executed')
            print('DatabaseMigration completed')
            print('Starting Database update')
            from initialize_common import InitializeCommon
            InitializeCommon.update_db(InitializeCommon())
            print('Database update completed')
            from plugin_dbscripts import PluginScripts
            print('Starting Plugin DB scripts execution.')
            PluginScripts.initialize(PluginScripts())
            print('Plugin DB scripts execution completed')
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    def start_components(self):
        """Start the individual components."""
        try:
            lggr.debug('Starting all components')
            import plugin
            import gateway
            import web
            from scheduler_operations import SchedulerOperations
            lggr.debug('Starting plugins')
            plugin = plugin.Plugin('--start plugins'.split(), self.conf_data)
            plugin.operation()
            lggr.debug('Starting gateway')
            comp_stat = './appviewx --status plugins'
            print (colored(
                "Waiting for avx_platform_core to be started(It may take upto 2 mins)",
                "cyan"))
            lggr.debug(
                "Waiting for avx_platform_core to be started(It may take upto 2 mins)")
            t_end = time.time() + 60 * 2
            while time.time() < t_end:
                ps = subprocess.Popen(comp_stat, shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
                result = ps.communicate()[0].decode("utf-8")
                if 'Not Running' not in result:
                    lggr.debug('avx-common in Not Runnning')
                    break

            gateway = gateway.Gateway(
                '--start gateway'.split(), self.conf_data)
            gateway.operation()
            lggr.debug('Starting web')
            web = web.Web('--start web'.split(), self.conf_data)
            web.operation()
            lggr.debug('Starting scheduler process')
            self.conf_data = config_parser(self.conf_file)
            comp_stat = './appviewx --status gateway'
            print (colored(
                "Waiting for avx_platform_gateway to be started(It may take upto 2 mins)",
                "cyan"))
            lggr.debug(
                "Waiting for avx_platform_gateway to be started(It may take upto 2 mins)")
            t_end = time.time() + 60 * 2
            while time.time() < t_end:
                ps = subprocess.Popen(comp_stat, shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
                result = ps.communicate()[0].decode("utf-8")
                if 'Not Running' not in result:
                    lggr.debug('Gateway in Not Runnning')
                    break
            ob = SchedulerOperations(['--start', 'scheduler'], self.conf_data)
            ob.operation()
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

    def install(self):
        """Start installation."""
        try:
            lggr.info('Checking if license and data folder (not) present')
            self.license_and_data_folder_check()
            lggr.info('Checking prerequisite check')
            self.prerequisite()
            lggr.info('Starting the initialization process')
            self.extract_logstash()
            self.initialization()
            lggr.info('Starting the mongodb')
            self.dbstart()
            lggr.info('Updating the scheduler port in conf file')
            scheduler_port = self.conf_data['COMMONS']['scheduler_port'][0]
            cmd_to_kill_scheduler_process = 'kill -9 `lsof -t -i:' +\
                scheduler_port + '`'
            subprocess.run(cmd_to_kill_scheduler_process + ' >/dev/null 2>&1',
                           shell=True)
            try:
                primary_db_host = avx_commons.primary_db(self.conf_data)
                primary_db_ip = primary_db_host.split(':')[0]
            except:
                primary_db_ip = self.hostname
            self.update_scheduler_port(self.conf_data, primary_db_ip)
            lggr.info('Starting the dbimport and jarmigration')
            self.dbimport_and_jarmigration()
            self.remove_role_template()
            lggr.info('Starting individual components')
            self.start_components()
            from updateconf import UpdateConf
            ob = UpdateConf(fresh=True)
            ob.initialize()
            lggr.info('Starting avx_cert_gen')
            avx_cert_gen.initialise()
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            node = self.hostname
            user, path = avx_commons.get_username_path(
                self.conf_data, node)
            lggr.debug('Starting monitor script on ' + node)
            from scheduler_monitor import SchedulerMonitor
            SchedulerMonitor.check_monitoring_process(SchedulerMonitor())
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

if __name__ == '__main__':
    lggr.debug('Starting the AppViewX installation process')
    ob = AppViewXInstall()
    ob.install()
    lggr.debug('AppViewX installed successfully')
