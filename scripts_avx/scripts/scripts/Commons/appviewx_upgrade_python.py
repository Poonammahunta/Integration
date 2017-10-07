"""Script to upgrade the AppViewX from earlier version."""
import os
import sys
import socket
import logger
import signal
import getpass
import subprocess
import avx_commons
from time import time
from time import sleep
from config_parser import config_parser
from avx_commons import get_username_path
from using_fabric import AppviewxShell
from avx_commons import return_status_message_fabric
from appviewx_install_python import AppViewXInstall
lggr = logger.avx_logger('appviewx_upgrade_python')
hostname = socket.gethostbyname(socket.gethostname())
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../upgrade')
sys.path.insert(0, current_file_path + '/../Mongodb')
from mongodb_setup import print_success


class AppViewXUpgrade():
    """Class to upgrade the AppViewX from older versions."""

    """Steps include in upgradation:
    Steps done before the execution of this script:
        1. Copy the packages to their location
        2. Conf-Merge operation
        3. Getting the migration data details from the DB
    Operations done by this script:
        1. Initialize all components
        2. Start DB (with/without authentication based upon the older version)
        3. DBImport from the older version to the current version.
        4. JarMigration operatio from the older version to the current version.
        5. Start the individual components."""

    def __init__(self, version):
        """The function to define the class variables."""
        self.conf_file = os.path.abspath(
            current_file_path + '/../../conf/appviewx.conf')
        self.conf_data = config_parser(self.conf_file)
        self.version = version
        self.install_ob = AppViewXInstall()
        self.appviewx_installed_location = os.path.abspath(
            current_file_path + '/../../')

    def initialization(self):
        """."""
        lggr.debug('Starting prerequisite check.')
        self.install_ob.prerequisite()
        print()
        self.install_ob.extract_logstash()
        lggr.debug('Starting initialization.')
        self.install_ob.initialization()

    def start_db(self):
        """."""
        import mongodb
        if self.version >= str(10.7):
            mongo_ob = mongodb.MongoDB(
                ['--start', 'mongodb'], self.conf_data, auth=True)
            lggr.info('Starting the Mongodb with authentication')
            lggr.debug('Starting the Mongodb without authentication')
            mongo_ob.operation()
        else:
            mongo_ob = mongodb.MongoDB(
                ['--start', 'mongodb'], self.conf_data, auth=False)
            lggr.info('Starting the Mongodb with authentication')
            lggr.debug('Starting the Mongodb without authentication')
            mongo_ob.operation()
        cmd_for_premigration_data = current_file_path +\
            '/../../Python/bin/python ' + current_file_path +\
            '/db_migration_check.py pre ' +\
            self.conf_file
        ps = subprocess.run(cmd_for_premigration_data, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ps.returncode:
            lggr.error('Unable to get pre migration data!')
            print('Unable to get pre migration data!')

    def dbimport(self):
        """."""
        lggr.debug('Starting dbimport from version: ' + self.version)
        user, path = get_username_path(self.conf_data, self.priamry_db_host)
        cmd_for_dbimport = path + '/Python/bin/python ' + path +\
            '/scripts/Mongodb/mongodb_setup.py --dbimport upgrade ' +\
            self.version
        print_success('Release scripts Execution', 'Started')
        fab_ob = AppviewxShell([self.priamry_db_host], user=user)
        ps = fab_ob.run(cmd_for_dbimport)
        stat, res = return_status_message_fabric(ps)
        if stat:
            print(res.rstrip())

    def jarmigration(self):
        """."""
        lggr.debug('Starting jar migration from: ' + self.version)
        user, path = get_username_path(self.conf_data, self.priamry_db_host)
        print_success('Database Migration', 'Started')
        cmd_for_jarmigration = path + '/Python/bin/python ' + path +\
            '/scripts/Mongodb/mongodb_setup.py --jarmigration upgrade ' +\
            self.version
        fab_ob = AppviewxShell([self.priamry_db_host], user=user)
        ps = fab_ob.run(cmd_for_jarmigration)
        stat, res = return_status_message_fabric(ps)
        if stat:
            print(res.rstrip())
            print()

        lggr.debug('Running the license jars.')

        print_success('Database Update', 'Started')
        from initialize_common import InitializeCommon
        InitializeCommon.update_db(InitializeCommon())
        print_success('Database Update', 'Completed')
        print()
        from plugin_dbscripts import PluginScripts
        print_success('Plugin DB scripts Execution', 'Started')
        PluginScripts.initialize(PluginScripts())
        print_success('Plugin DB scripts Execution', 'Completed')
        print()

    def execute_license_jars(self):
        """."""
        migrator_jar_location = self.appviewx_installed_location +\
            '/avxgw/acf-migrator-1.0.0.jar'
        appviewx_properties = self.appviewx_installed_location +\
            '/properties/'
        framework_jar_location = self.appviewx_installed_location +\
            '/Plugins/framework/framework-db.jar'
        logs_home = self.appviewx_installed_location + '/logs/ '
        java_location = self.appviewx_installed_location + '/jre/bin/java '
        admin_jar_location = self.appviewx_installed_location +\
            '/avxgw/acf-admin-1.0.0.jar'
        migrator_jar_command = java_location + ' -Davx_logs_home=' +\
            logs_home + ' -cp ' + migrator_jar_location + ':' +\
            framework_jar_location + ':' + appviewx_properties +\
            ' com.appviewx.acfmigrator.main.AcfMigratorMain &'
        acf_admin_jar_command = java_location + ' -Davx_logs_home=' +\
            logs_home + ' -cp ' + admin_jar_location + ':' +\
            framework_jar_location + ':' + appviewx_properties +\
            ' com.appviewx.acfadmin.main.AcfAdminMain &'
        ip = hostname
        user = getpass.getuser()
        fab_obj = AppviewxShell([ip], user=user)
        fab_obj.run(migrator_jar_command)
        fab_obj.run(acf_admin_jar_command)

    def start_components(self):
        """."""
        lggr.debug('Starting all components.')
        self.install_ob.start_components()

    def empty_patch(self):
        """."""
        from using_fabric import AppviewxShell
        for ip, user, path in zip(self.conf_data['ENVIRONMENT']['ips'],
                                  self.conf_data['ENVIRONMENT']['username'],
                                  self.conf_data['ENVIRONMENT']['path']):
            fab_ob = AppviewxShell([ip], user=user)
            if self.version > '11.0':
                cmd = 'rm -rf ' + path + '/patch/*'
            else:
                cmd = 'rm -rf ' + path + '/patch/* ' + path + '/zookeeper ' +\
                    path + '/elasticsearch'
            fab_ob.run(cmd)

    def upgrade(self):
        """."""
        self.initialization()
        scheduler_port = self.conf_data['COMMONS']['scheduler_port'][0]
        cmd_to_kill_scheduler_process = 'kill -9 `lsof -t -i:' +\
            scheduler_port + '`'
        subprocess.run(cmd_to_kill_scheduler_process + ' >/dev/null 2>&1',
                       shell=True)
        self.install_ob.update_scheduler_port(self.conf_data, hostname)
        print()
        self.start_db()
        sleep(4)
        print()
        from avx_commons import primary_db
        t_end = time() + 60
        self.priamry_db_host = None
        while time() < t_end:
            try:
                self.priamry_db_host = primary_db(self.conf_data).split(':')[0]
            except:
                lggr.debug('Some error in getting primary DB details.')
                self.priamry_db_host = None
                sleep(2)
        if not self.priamry_db_host:
            self.priamry_db_host = hostname
            lggr.debug('Unable to get primary db details so ' +
                       'executing the scripts on localhost')
        self.dbimport()
        print()
        self.jarmigration()
        self.execute_license_jars()
        self.start_components()
        cmd_for_postmigration_data = current_file_path +\
            '/../../Python/bin/python ' + current_file_path +\
            '/db_migration_check.py post ' +\
            self.conf_file
        ps = subprocess.run(cmd_for_postmigration_data, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ps.returncode:
            lggr.error('Unable to get post migration data!')
            print('Unable to get post migration data!')
        from updateconf import UpdateConf
        ob = UpdateConf(fresh=True)
        ob.initialize()
        import avx_cert_gen
        lggr.debug('Initializing initial certificates.')
        avx_cert_gen.initialise()
        lggr.debug('Starting monitor utility')
        from scheduler_monitor import SchedulerMonitor
        SchedulerMonitor.check_monitoring_process(SchedulerMonitor())
        self.empty_patch()

        print('Upgrade Completed')

if __name__ == '__main__':
    arg = sys.argv[-1]
    ob = AppViewXUpgrade(arg)
    ob.upgrade()
