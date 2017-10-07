"""The script to start MongoDB across the nodes."""
import os
import sys
import time
import signal
import logger
import socket
import traceback
import avx_commons
from termcolor import colored
from config_parser import config_parser
from appviewx_install_python import AppViewXInstall
lggr = logger.avx_logger('dbstart')
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Mongodb/')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class DbStart():
    """DB start class."""

    """The class is used to start MongoDB
    across the nodes as specified in the conf file.
    The following steps re followed in order to stop MongoDB:
    1. Start MongoDB without authentication.
    2. Push authentication
    3. Stop mongodb
    4. Start MongoDB with authentication."""

    def __init__(self):
        """The method to define the class variables."""
        try:
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.python_path = '/Python/bin/python'
            self.script_path = '/scripts'
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

    def check_data_folder(self):
        """The function to abort if db folder is already present."""
        data_path = '/db/mongodb/data/db'
        to_exit = 0
        for ip in self.conf_data['MONGODB']['ips']:
            user, path = avx_commons.get_username_path(self.conf_data, ip)
            index = self.conf_data['ENVIRONMENT']['ips'].index(ip)
            conn_port = str(
                self.conf_data['ENVIRONMENT']['ssh_port'][index])
            if ip == self.hostname:
                cmd = ''
            else:
                cmd = 'ssh -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + user + '@' + ip
            lggr.debug('Checking for data folder on ' + ip)
            cmd = cmd + ' "ls -l ' + path + data_path + ' | wc -l"'
            ps = AppViewXInstall.execute_command(cmd)
            if ps.stderr:
                print('Data folder not present on ' + ip)
                lggr.error('Data folder not present on ' + ip)
                to_exit = 1
            elif int(ps.stdout.decode()) > 1:
                print('AppViewX already Installed!')
                print('Empty the data/db folder present on ' + ip)
                lggr.error('AppViewX already installed.')
                to_exit = 1
        if to_exit:
            sys.exit(1)

    def adduser(self, db_ips, db_ports, do_adduser=True, primary_ip=''):
        """The method to add user in the DB."""
        """This process is done after DB is started without authentication."""
        user, appviewx_dir = avx_commons.get_username_path(self.conf_data,
                                                           self.hostname)
        # Making sure that the DB is up before pushing authentication.
        lggr.debug('Waiting for Mongo to start withou authentication.')
        time.sleep(10)
        lggr.debug('Pushing replica set into the DB.')
        repset = avx_commons.replica_set(appviewx_dir, self.conf_data)
        if repset:
            lggr.debug('replica set pushed successfully')
        else:
            lggr.debug('Unable to push replica set')
            lggr.error('Unable to push replica set')
        t_end = time.time() + 60 * 2
        from avx_commons import mongo_status
        while time.time() < t_end:
            try:
                mongodb_stat = mongo_status(db_ips[0], db_ports[0])
            except Exception:
                error = str('\n'.join(
                    traceback.format_exception(*(sys.exc_info()))))
                print(colored(error, 'red'))
                lggr.error(error)
                sys.exit(1)
            if 'not_running' not in mongodb_stat and 'no_replication'\
                    not in mongodb_stat and 'no_primary' not in mongodb_stat:
                lggr.error('Error in Mongodb operation')
                break
        from avx_commons import primary_db, get_db_credentials
        db_host = primary_db(self.conf_data)
        db_ip, db_port = db_host.split(':')
        db_username, db_password, db_name = get_db_credentials()
        mongo = appviewx_dir + 'db/mongodb/bin/mongo'
        # Making sure the replica set has been pushed.
        time.sleep(5)
        if do_adduser:
            lggr.debug('adduser.js needs to be pushed.')
            adduser_cmd = mongo + ' ' + db_host + '/admin --quiet ' +\
                appviewx_dir + '/scripts/Commons/adduser.js'
            lggr.debug('cmd for adduser: ' + adduser_cmd)
            lggr.debug('Tring to push adduser.js')
            ps = AppViewXInstall.execute_command(adduser_cmd)
            if ps.returncode:
                lggr.error('Unable to push adduser.js')
            else:
                lggr.debug('adduser.js pushed into the DB')

    def start(self, force_primary=False, primary_ip='', do_adduser=True):
        """The function to facilitate the starting of DB."""
        lggr.debug('Trying to start DB')
        db_ips = self.conf_data['MONGODB']['ips'][0]
        db_ports = self.conf_data['MONGODB']['ports'][0]
        mongodb_stat = avx_commons.mongo_status(db_ips, db_ports,
                                                authentication=True)
        if 'not_running' not in mongodb_stat:
            lggr.error('Mongodb is already running')
            sys.exit('MongoDB is already running')
        username, path = avx_commons.get_username_path(self.conf_data,
                                                       self.hostname)
        lggr.debug('Checking for license file and data folder')

        lggr.debug('Starting mongodb')
        user_input = ['--start', 'mongodb', 'all']
        import mongodb
        mongo = mongodb.MongoDB(user_input, self.conf_data, auth=False)
        try:
            mongo.operation()
        except Exception:
            error = str('\n'.join(
                traceback.format_exception(*(sys.exc_info()))))
            print(colored(error, 'red'))
            lggr.error(error)
            sys.exit(1)

        lggr.debug('completed db_start module without authentication')
        t_end = time.time() + 60 * 2
        lggr.debug('Checking the status of Mongodb')
        while time.time() < t_end:
            mongodb_stat = avx_commons.mongo_status(db_ips, db_ports)
            if 'not_running' not in mongodb_stat:
                lggr.error('Mongodb not Running')
                break
        lggr.debug('calling adduser with primary ip ' + primary_ip +
                   ' to force replication')
        #if self.hostname == self.conf_data['MONGODB']['ips'][0]:
        self.adduser([db_ips], [db_ports], do_adduser)

        # Restarting DB after pushing authentication.

        argument_input = ['--restart', 'mongodb']
        lggr.debug('Restarting Mongodb')
        lggr.info('Restarting Mongodb')
        mongo = mongodb.MongoDB(argument_input, self.conf_data, auth=True)
        mongo.operation()
        t_end = time.time() + 60 * 2
        lggr.debug('Checking the status of Mongodb')
        while time.time() < t_end:
            mongodb_stat = avx_commons.mongo_status(db_ips, db_ports, True)
            if 'not_running' not in mongodb_stat and 'no_replication' not in\
                    mongodb_stat and 'no_primary' not in mongodb_stat:
                lggr.error('Mongodb not Running')
                break

    def initialize(self):
        """The function to call the start function."""
        """This function is the interface to outer scripts."""
        self.check_data_folder()
        self.start()

if __name__ == '__main__':
    ob = DbStart()
    ob.initialize()
