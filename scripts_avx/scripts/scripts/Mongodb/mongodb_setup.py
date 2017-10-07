import os
import sys
import time
import argparse
from configobj import ConfigObj
import inspect
import subprocess
import socket
import termcolor
from time import strftime
import getpass
import inspect
import logging
from termcolor import colored
sys.path.insert(0, 'Commons')

if not os.path.realpath('Commons/') in sys.path:
    sys.path.append(os.path.realpath('Commons/'))
if not os.path.realpath('Mongodb/') in sys.path:
    sys.path.append(os.path.realpath('Mongodb/'))
if not os.path.realpath('Web/') in sys.path:
    sys.path.append(os.path.realpath('Web/'))
if not os.path.realpath('Gateway/') in sys.path:
    sys.path.append(os.path.realpath('Gateway/'))
if not os.path.realpath('Plugins/') in sys.path:
    sys.path.append(os.path.realpath('Plugins/'))
from config_parser import config_parser
from avx_commons import primary_db,db_connection,get_db_credentials
conf_data = config_parser(os.path.dirname(os.path.realpath(__file__)) + '/../../conf/appviewx.conf')
import set_path
import avx_commons
hostname = socket.gethostbyname(socket.gethostname())
current_username = getpass.getuser()
current_file = inspect.getfile(inspect.currentframe())
position = current_username + '@' + hostname + '-' + current_file
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('dbimport script')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
def help_fun():
        print(" ERROR in user_input:")
        print(" \t\t 1) ./appviewx --databasemigration fresh")
        print(" \t\t 2) ./appviewx --databasemigration upgrade <old_version>")
        print(" \t\t 1) ./appviewx --databasemigration status fresh")
        print(" \t\t 2) ./appviewx --databasemigration status upgrade")
        sys.exit(1)

def db_import_help_fun():
        print(" ERROR in user_input:")
        print(" \t\t 1) ./appviewx --databaseimport fresh")
        print(" \t\t 2) ./appviewx --databaseimport upgrade <old_version>")
        print(" \t\t 1) ./appviewx --databaseimport status fresh")
        print(" \t\t 2) ./appviewx --databaseimport status upgrade")
        sys.exit(1)

def db_status_help_fun():
        print(" ERROR in user_input:")
        print(" \t\t 1) ./appviewx --databaseimport status fresh")
        print(" \t\t 2) ./appviewx --databaseimport status upgrade")
        print(" \t\t 1) ./appviewx --databasemigration status fresh")
        print(" \t\t 2) ./appviewx --databasemigration status upgrade")
        sys.exit(1)

def variable_setup():
        global primary_ip,primary_port,username,password,auth_db,mongoname
        try:
          primarydb = primary_db(conf_data,status=True)
          primary_ip,primary_port = primarydb.split(':')
          lggr.debug('Obtained primary db details')
        except:
          print (colored("Error in fetching primarydb details","red"))
          lggr.error('Error in fetching primarydb ip and port')
          sys.exit(1)

        try:
           username,password,auth_db = get_db_credentials()
           lggr.debug('Obtained primarydb username and password')
        except Exception:
           print (colored("Error in fetching DB user details","red"))
           lggr.error('Error in fetching primary db user details')
           sys.exit(1)
        mongoname = avx_path.db_bin_path + 'mongo'
        mongo_status = 'cd ' + avx_path.appviewx_path + 'scripts/ && ./appviewx --status mongodb '
        if not conf_data['ENVIRONMENT']['multinode'][0].lower() == 'true':
           status = subprocess.run(mongo_status, shell=True,
                                   stdout=subprocess.PIPE).stdout.decode("utf-8")
           if not '[PRIMARY]' in status:
              print(colored('Mongodb is not running','red'))
              sys.exit(1)


def print_success(first_value, second_value):
    """."""
    print('{0:35s} {1:15s} {2:15s} {3:40s}'.format(first_value, ' ', ' ', second_value))

class MongoDatabase(object):

    def __init__(self):
        variable_setup()

    @staticmethod
    def populate_data(
            file,dbname='appviewx'):
        '''To get the command to run the db scripts'''
        data_fill =''
        if file.endswith('.js'):
            data_fill = mongoname + ' ' + primary_ip + ':' + primary_port + '/' + dbname +  ' -u ' + username + \
                ' -p ' + password + ' --authenticationDatabase ' + auth_db + ' --quiet ' + file

        elif file.endswith('.jar'):
            location = Getfiles.current_frame()
            if not 'external-auth-systems-migration-1.0.0.jar' in file:
                data_fill = location + '/../../jre/bin/java -jar ' + file + \
                ' ' + location + '/../../properties/appviewx.properties'
            else:
                data_fill = location + '/../../jre/bin/java -jar ' + ' -Dappviewx.property.path=' + location + '/../../properties/ ' +file
        return data_fill

    @staticmethod
    def migration_jar_execution(javahome, property_path, file):
        '''To get the command to execute the migration jar '''
        data_fill = javahome + ' ' + property_path + ' ' + file
        return data_fill

    @staticmethod
    def get_master_scripts(location):
        master_scripts_location = location + '/../../release_scripts/Master_Scripts/db_scripts/'
        lggr.debug('Verifying the presence of master scripts')
        if not os.path.exists(master_scripts_location):
            lggr.error('Master scripts is absent')
            return None
        else:
            lggr.debug('master scripts is available')
            return os.listdir(master_scripts_location)

    def push_master_scripts(self):
        try:
            release_data = dict()
            release_data['_id'] = 'Master_scripts'
            release_data['files'] = list()
            location = Getfiles.current_frame()
            try:
                files = self.get_master_scripts(location)
                lggr.debug('obtained master scripts')
            except Exception as e:
                lggr.error(e)
                print (colored('Master scripts directory is absent','red'))
                sys.exit(1)
            if files:
                for script in files:
                    release_data['Executed_time'] = strftime(
                        "%Y-%m-%d %H:%M:%S")
                    content = self.populate_data(location + '/../../release_scripts/Master_Scripts/db_scripts/'+ script)
                    output = Getfiles.execute_command(content)
                    release_data['files'].append(script)
                import json
                release_data = json.dumps(release_data)
                lggr.debug('Master scripts are executed and now pushing details into the db')
                with open(location + '/.master_scripts.js', 'w') as out_file:
                    out_file.write(
                        'db.system_files_executed.save(' + str(release_data) + ')')
                command = self.populate_data(location + '/.master_scripts.js')
                Getfiles.execute_command(command)
            else:
                print ("Master scripts directory is empty please do verify the files")
                sys.exit(1)
        except KeyboardInterrupt:
            lggr.error('user has given a keyboard interrupt')
            sys.exit(1)
        except Exception as e:
            print (e)
            print ('Error in executing Master scripts')
            sys.exit(1)
        print_success('Master Scripts Execution', 'Completed')


class Getfiles(object):

    def __init__(self):
        variable_setup()

    @staticmethod
    def current_file():
        '''This function is to get the current file name'''
        current_file = inspect.getfile(inspect.currentframe())
        return current_file

    @staticmethod
    def current_frame():
        '''This function can be used to get the current directory in which the script is running'''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        return current_directory

    def check_release_scripts(self):
        '''This function is used to check if the release_scripts directory is available'''
        lggr.info('checking for avalibality on release_scripts for core appviewx')
        lggr.debug('checking for avalibality on release_scripts for core appviewx')
        location = self.current_frame()
        release_scripts_path = location + '/../../release_scripts'
        if os.path.exists(release_scripts_path):
            return True
        else:
            return False

    @staticmethod
    def execute_command(command,return_data = False):
        try:
            ps = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            lggr.debug('Executing command: %s' % command.replace('-p ' + password, '-p xxxxxxxx'))
            result = True
            output = ps.stdout.decode("utf-8")
            """if 'failed to load' in output[0].decode("utf-8").lower()  and 'SyntaxError' in output[0].decode("utf-8"):
                print (colored('Error in executing command: %s' % command,'red'))
                lggr.error('Error in executing command: %s' % command)
                lggr.error('Error : %s' % output[0].decode("utf-8"))
                result = False"""
            if ps.returncode:
                print (colored('Error in executing command: %s' % command, 'red'))
                lggr.error('Error in executing command: %s' % command)
                lggr.error('Error : %s' % output)
                result = False

            if return_data:
                return result
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print (e)
            print ("Error in executing the command" + output)
            sys.exit(1)
        return output

    def microservices_files(self):
        ''' To get the details on the microservices '''
        location = self.current_frame
        subsystems_location = location + '/../../Microservices'
        subsystems = os.listdir(Modules_location)
        return subsystems

    @staticmethod
    def subsystem_bound(subsystem_name, location):
        '''To determine whether the given jar is northbound or southbound'''
        subsystems_location = location + '/' + subsystem_name
        files = os.listdir(subsystems_location)
        for file in files:
            if file.startswith('Release_'):
                bound = 'north'
                break
            else:
                bound = 'south'
        return bound

    def get_release_scripts_version(self,base_version,upgrade):
        if upgrade.upper() == 'FALSE':
            release_scripts_location = self.current_frame()
            release_scripts_location = release_scripts_location + '/../../release_scripts'
            release_versions = os.listdir(release_scripts_location)
            for version in release_versions:
                if not version.startswith('Release'):
                    release_versions.remove(version)
            return release_versions
        else:
            release_scripts_location = self.current_frame()
            release_scripts_location = release_scripts_location + '/../../release_scripts/'
            release_versions = os.listdir(release_scripts_location)
            if not base_version:
                print ("Please do mention the base version to execute the fresh scripts")
                sys.exit(1)
            new_release_version = list()
            for version in release_versions:
                if version.startswith('Release_'):
                    version_number = version.strip('Release_')
                    if version_number > base_version:
                        new_release_version.append(version)
            if new_release_version:
                lggr.debug(new_release_version)
            return new_release_version

    def execute_release_scripts(self, release_versions,base_version=False):
       
        location = self.current_frame()
        release_data = {}
        if not base_version:
           release_data['_id'] = 'db_import_Fresh'
        else:
           release_data['_id'] = 'db_import_Upgrade'
        release_data['Executed_versions'] =[]
        ip = primary_ip
        port = primary_port
        for version in release_versions:
            lggr.debug('Executing scripts for version:' + version)
            executing_version = version
            executing_version = executing_version.replace('.', '_')
            release_scripts_location = location + '/../../release_scripts/' + version + '/db_scripts'
            if not os.path.exists(release_scripts_location):
                print(termcolor.colored('The scripts for the version ' + version +
                      ' is not available in the release directory ', "yellow"))
                lggr.debug('The scripts for the version ' + version +' is not available in the release directory ')
                continue
            db_names = os.listdir(release_scripts_location)
            version_names = dict()
            version_names['files']=list()
            version_names['Version'] = version
            version_names['Executed_time'] = time.strftime("%d/%m/%Y - %I:%M:%S")
            files = []
            for db in db_names:
                scripts_location = os.listdir(
                    release_scripts_location + '/' + db)
                dbname = db
                for script in scripts_location:
                    command = MongoDatabase.populate_data(
                        release_scripts_location + '/' + db + '/' + script,dbname)
                    version_names['files'].append(script)
                    self.execute_command(command)
            release_data['Executed_versions'].append(version_names) 
        import json
        release_data = json.dumps(release_data)
        if not base_version:
          file_name = avx_path.appviewx_path + '/scripts/Mongodb/.dbimport_Fresh.js'
          lggr.debug('dumping the data regarding the executed release scripts into the db')
          with open(avx_path.appviewx_path + '/scripts/Mongodb/.dbimport_Fresh.js', 'w') as out_file:
            out_file.write(
                'db.system_files_executed.save(' + str(release_data) + ')')
        else:
          file_name = avx_path.appviewx_path + '/scripts/Mongodb/.dbimport_Upgrade'  + '.js'
          with open(avx_path.appviewx_path + '/scripts/Mongodb/.dbimport_Upgrade.js', 'w') as out_file:
            out_file.write(
                'db.system_files_executed.save(' + str(release_data) + ')')
        command = MongoDatabase.populate_data(
            file_name,'appviewx')
        self.execute_command(command)
        print_success('Release Scripts Execution', 'Completed')
        lggr.debug('Execution of release scripts is completed')
        lggr.info('Execution of release scripts is completed')

    def execute_migration_scripts(
            self,
            release_versions,
            base_version,
            upgrade):
        release_data = dict()
        executed_list, exe_time = self.executed_status()
        migration_status = {}
        migration_status['files'] = []
        migration_status['_id'] = 'executed_migration_files'
        migration_status['Executed_time'] = []
        for each_file in exe_time:
            migration_status['Executed_time'].append(each_file)
        if os.path.exists(avx_path.appviewx_path + 'scripts/.jar_executed_status.txt'):
            with open(avx_path.appviewx_path + 'scripts/.jar_executed_status.txt') as fd:
                data = fd.readlines()
                data = [x.strip('\n')for x in data]
                executed_list = executed_list + data
        if upgrade.upper() == 'TRUE':
            release_data['_id'] = 'jarmigration_Upgrade'
            release_data['Executed_versions'] = []
            target_version = conf_data['COMMONS']['version'][0]
            target_version = target_version.strip('V')
            upgrade_version = 'Release_' + target_version
            location = self.current_frame()
            new_release_version = list()
            ip = primary_ip
            port = primary_port
            for version in release_versions:
                version_check = version.strip('Release_')
                if version_check > base_version:
                    new_release_version.append(version)
            lggr.debug("obtained the release versions which are to be executed")
            lggr.debug(new_release_version)
            for version in new_release_version:
                lggr.debug('Current executing version is ' + version)
                executing_version = version
                current_version = version.strip('Release_')
                if True:
                    version_names = dict()
                    version_names['files'] = list()
                    version_names['Version'] = current_version
                    version_names['Executed_time'] = time.strftime("%d/%m/%Y - %I:%M:%S")
                    files = []
                    release_scripts_location = location + '/../../release_scripts/' + version + '/migration_scripts'
                    if os.path.exists(release_scripts_location):
                        migration_scripts = os.listdir(release_scripts_location)
                        if migration_scripts:
                            lggr.debug('Obtained migration scripts')
                            lggr.debug(migration_scripts)
                        for script in migration_scripts:
                            if script in executed_list:
                                continue
                            command = MongoDatabase.populate_data(
                                release_scripts_location + '/' + script)
                            result = self.execute_command(command, return_data=True)
                            if result:
                                executed_list.append(script)
                                migration_status['Executed_time'].append(script + ' @ ' + time.strftime("%d/%m/%Y - %I:%M:%S"))
                            version_names['files'].append(script)
                    release_data['Executed_versions'].append(version_names)
            import json
            release_data = json.dumps(release_data)
            with open(avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Upgrade.js', 'w') as out_file:
                out_file.write(
                    'db.system_files_executed.save(' + str(release_data) + ')')
            command = MongoDatabase.populate_data(avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Upgrade.js','appviewx')
            self.execute_command(command)
            # print_success('Database migration scripts Execution', 'Completed')
            lggr.debug("Executed mongo migration scripts for " + version)
        else:
            release_data['_id'] = 'jarmigration_Fresh'
            release_data['Executed_versions'] = []
            location = self.current_frame()
            target_version = conf_data['COMMONS']['version'][0]
            target_version = target_version.strip('V')
            upgrade_version = 'Release_' + target_version
            lggr.debug('Version to be executed is ' + upgrade_version)
            release_scripts_location = avx_path.release_scripts_path + upgrade_version + '/fresh'
            version_names = dict()
            files = []
            import json
            version_names['Version'] = upgrade_version
            version_names['files'] = []
            release_data['Executed_time'] = time.strftime("%d/%m/%Y - %I:%M:%S")
            if not os.path.exists(release_scripts_location):
                release_data['Executed_versions'].append(version_names)
                release_data = json.dumps(release_data)
                with open(avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Fresh.js', 'w') as out_file:
                 out_file.write(
                    'db.system_files_executed.save(' + str(release_data) + ')')
                command = MongoDatabase.populate_data(avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Fresh.js','appviewx')
                self.execute_command(command)
                print (termcolor.colored(
                    "%s directory is not found in the local environment" % release_scripts_location,"yellow"))
                return
            migration_scripts = os.listdir(release_scripts_location)
            executing_version = upgrade_version
            executing_version = executing_version.replace('.', '_')
            ip = primary_ip
            port =primary_port
            config_data = dict()
            if os.path.exists(release_scripts_location + '/jar_execution_params.txt'):
               config_data = ConfigObj(release_scripts_location + '/jar_execution_params.txt')
            for script in migration_scripts:
                if script in executed_list:
                   continue
                if script.endswith('.jar'):
                   params = ''
                   if script in config_data.keys():
                      params = config_data[script]
                      params = params.replace('{AVX_HOME}',avx_path.appviewx_path)
                   if script == 'StoreHelperScripts.jar':
                      command = avx_path.java_path + ' -Dappviewx.property.path=' +  avx_path.appviewx_path + '/properties/ -jar ' + release_scripts_location + '/' + script + ' ' + avx_path.appviewx_path + '/aps/defaultHelperScripts/'
                   else:
                      command = avx_path.java_path + ' -jar ' + release_scripts_location + '/' + script + ' ' + params
                elif script.endswith('.js'):
                   command = MongoDatabase.populate_data(
                    release_scripts_location + '/' + script)
                else:
                    continue
                result = self.execute_command(command,return_data = True)
                if result:
                   executed_list.append(script)
                   migration_status['Executed_time'].append(script + ' @ ' + time.strftime("%d/%m/%Y - %I:%M:%S"))
                version_names['files'].append(script)
            release_data['Executed_versions'].append(version_names)
            import json
            release_data = json.dumps(release_data)
            with open(avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Fresh.js', 'w') as out_file:
                out_file.write(
                    'db.system_files_executed.save(' + str(release_data) + ')')
            command = MongoDatabase.populate_data(
                avx_path.appviewx_path + '/scripts/Mongodb/.jarmigration_Fresh.js','appviewx')
            self.execute_command(command)
            print_success('Mongo migration scripts Execution', 'Completed')
        migration_status['files'] = executed_list
        release_data = json.dumps(migration_status)
        with open(avx_path.appviewx_path + '/scripts/Mongodb/.migration_files_executed.js', 'w') as out_file:
                out_file.write(
                    'db.system_files_executed.save(' + str(release_data) + ')')
        command = MongoDatabase.populate_data(
                avx_path.appviewx_path + '/scripts/Mongodb/.migration_files_executed.js','appviewx')
        self.execute_command(command)
        print_success('Database Migration', 'Completed')
        lggr.debug('Executing jar migration is completed')

    def microservices_scripts(self, upgrade=None):
        '''
        '''
        location = self.current_frame()
        microservices_location = location + '/../plugins/'
        if not os.path.exists(microservices_location):
            print ("Plugins is not available here")
            sys.exit(1)
        else:
            subsystems = self.microservices_files()
            for system in subsystems:
                bound = subsystem_bound(
                    Getfiles(), system, microservices_location)
                if bound.upper() == 'NORTH':
                    subsystem_files = os.listdir(
                        microservices_location + '/' + system)
                    for files in subsystem_files:
                        if not 'Release_' in files:
                            print (
                                "The release scripts is not present in the given format")
                            sys.exit(0)
                        else:
                            if not os.path.exists(
                                    microservices_location + '/' + files + '/db_scripts'):
                                print (
                                    "The db scripts is not available for the plugins")
                            else:
                                database_list = os.listdir(
                                    microservices_location + '/' + files + '/db_scripts')
                                for db in database_list:
                                    subsystem_release_scripts = os.listdir(
                                        microservices_location + '/' + files + '/db_scripts/' + db)
                                    for scripts in subsystem_release_scripts:
                                        mongoname = Getfiles.current_frame()
                                        command = MongoDatabase.populate_data(
                                            microservices_location +
                                            '/' +
                                            files +
                                            '/db_scripts/' +
                                            scripts)
                                        self.execute_command(command)
                elif bound.upper() == 'SOUTH':
                    print ("This is a south bound jar")

    def execute_gridfs_scripts(self):
        release_data = dict()
        release_data['_id'] = 'gridfs_scripts'
        release_data['files'] = list()
        location = self.current_frame()
        mongofiles = location + '/../../db/mongodb/bin/mongofiles '
        gridfs_location = location + '/../../release_scripts/GridFSDBInitialUploadFiles'
        gridfs_dbs = os.listdir(gridfs_location)
        for db in gridfs_dbs:
            release_data['executed_time'] = strftime("%Y-%m-%d %H:%M:%S")
            gridfs_files = os.listdir(gridfs_location + '/' + db)
            for files in gridfs_files:
                command = 'cd ' + gridfs_location + '/' + db + '; ' + mongofiles + ' --host ' + primary_ip + ':' + primary_port +  ' -u ' + username + \
                    ' -p ' + password + ' --authenticationDatabase ' +  auth_db + ' -d ' + db + ' -r put ' + files
                self.execute_command(command)
                release_data['files'].append(files)
        import json
        release_data = json.dumps(release_data)
        with open(avx_path.appviewx_path + '/scripts/Mongodb/.gridfs_scripts.js', 'w') as out_file:
            out_file.write(
                'db.system_files_executed.save(' + str(release_data) + ')')
        command = MongoDatabase.populate_data(
                avx_path.appviewx_path + '/scripts/Mongodb/.gridfs_scripts.js','appviewx')
        self.execute_command(command)
        print_success('Gridfs Scripts Execution', 'Completed')

    def import_fresh_scripts(self,base_version,upgrade):
        if self.check_release_scripts:
            lggr.debug('release_scripts directory is present')
            release_versions = sorted(self.get_release_scripts_version(base_version,upgrade))
            lggr.debug('obtained release versions')
            lggr.debug(release_versions)
        else:
            print (colored("Directory 'release_scripts is absent so dbimport is not gonna happen'","red"))
            lggr.error('release_scripts directory is absent')
            sys.exit(1)
        try:
         release_versions.remove('Master_Scripts')
         lggr.debug('removing Master_scripts from the default release_versions')
        except Exception:
         pass
        lggr.debug('calling funtion execute_release_scripts')
        self.execute_release_scripts(release_versions,base_version)
    def import_migration_jars(self,base_version,upgrade):
        if self.check_release_scripts():
            release_versions = sorted(self.get_release_scripts_version(base_version,upgrade))
            lggr.debug('obtained release versions')
            lggr.debug(release_versions)
            self.execute_migration_scripts(release_versions,base_version, upgrade)
            lggr.debug('Executed migration scripts')
        else:
            print (colored('Cannot find release version','red'))
            lggr.error('Directory release_scripts is absent')
            sys.exit(1)
    
    @staticmethod
    def get_jar_executed_status1(collection_name,ex_type = '',version=''):
        try:
         lggr.debug('connecting to mongodb')
         db_connect  = db_connection(conf_data,status=True)
         db_connect = db_connect['appviewx']['system_files_executed']
         collection_data = db_connect.find_one({'_id':'executed_migration_files'})
         lggr.debug('obtained collection data')
         for exec_file in collection_data['Executed_time']:
                print (colored('\t%s' % exec_file,"green"))
        except TypeError:
            if not version:
               print (termcolor.colored('%s are not executed for the fresh' % (ex_type),"red"))
            else:
               print (termcolor.colored('%s are not executed' % (ex_type),"red"))
        except Exception:
           print (termcolor.colored('Error in getting status from db',"red"))
           sys.exit(1)
    
    @staticmethod
    def get_jar_executed_status(collection_name,ex_type = '',version=''):
        try:
         lggr.debug('connecting to mongodb')
         db_connect  = db_connection(conf_data,status=True)
         db_connect = db_connect['appviewx']['system_files_executed']
         collection_data = db_connect.find_one({'_id':collection_name})
         lggr.debug('obtained collection data')
         print_once = True
         for exec_file in collection_data['Executed_versions']:
                if print_once and version == '':
                   print (termcolor.colored('files executed during DBimport(Fresh)','cyan')) 
                   print_once = False
                elif print_once and version:
                   print (termcolor.colored('files executed during DBimport(Migration)','cyan'))
                   print_once = False
                print (colored('%s \t %s' % (exec_file['Version'],exec_file['Executed_time']),'yellow'))
                for js_file in exec_file['files']:
                    print (colored("\t%s" % js_file,'green'))
        except TypeError:
            if not version:
               print (termcolor.colored('%s are not executed for the fresh' % (ex_type),"red"))
            else:
               print (termcolor.colored('%s are not executed for the upgrade' % (ex_type),"red"))
        except Exception:
           print (termcolor.colored('Error in getting status from db',"red"))
           sys.exit(1)
 
    @staticmethod
    def executed_status():
        try:
         lggr.debug('connecting to db')
         db_connect  = db_connection(conf_data,status=True)
         db_connect = db_connect['appviewx']['system_files_executed']
         collection_data = db_connect.find_one({'_id':'executed_migration_files'})
         lggr.debug('obtained collection data')
         if collection_data == None:
            return list(),list()
         return collection_data['files'],collection_data['Executed_time']
        except Exception:
         return []

if __name__ == '__main__':
   try:
    user_input = sys.argv[1:]
    lggr.debug('The user_input is ' + str(user_input))
    variable_setup()
    if len(user_input) > 1:
        if user_input[0] == '--dbimport':
            if user_input[1] == 'fresh':
                Getfiles.import_fresh_scripts(Getfiles(),'','false')
            elif user_input[1] == 'Master_Scripts':
                MongoDatabase.push_master_scripts(MongoDatabase())
            elif user_input[1] == 'gridfs':
                Getfiles.execute_gridfs_scripts(Getfiles())
            elif user_input[1] == 'upgrade':
                try:
                     release_dir_list = os.listdir(avx_path.release_scripts_path)
                except Exception as e:
                     print (termcolor.colored("release_scripts folder(%s) is not present in the local environment" % avx_path.release_scripts_path, "red"))
                     sys.exit(0)
                dir_check=[dir for dir in release_dir_list if dir.split('_')[-1]==user_input[2]]
                if not len(dir_check):
                    print (termcolor.colored("Release_directory for %s is not present in release_scripts" % user_input[2], "red"))
                    db_import_help_fun()
                base_version = user_input[2]
                Getfiles.import_fresh_scripts(Getfiles(),base_version,'true')
            elif user_input[1] == 'status':
                if user_input[2] == 'fresh':
                    Getfiles.get_jar_executed_status('db_import_Fresh','dbimport')
                elif user_input[2] == 'upgrade':
                    Getfiles.get_jar_executed_status('db_import_Upgrade','dbimport','upgrade')
        elif user_input[0] == '--jarmigration':
            if user_input[1] == 'fresh':
                Getfiles.import_migration_jars(Getfiles(),'' ,'false')
            if user_input[1] == 'upgrade':
                base_version = user_input[2]
                Getfiles.import_migration_jars(Getfiles(),base_version, 'true')
            elif user_input[1] == 'status':
                if user_input[2] == 'fresh':
                    print (termcolor.colored('files executed during Jarmigration(Fresh)','cyan'))
                    Getfiles.get_jar_executed_status1('executed_migration_files','Jarmigration')
                else:
                    print (termcolor.colored('files executed during Jarmigration(Migration)','cyan'))
                    Getfiles.get_jar_executed_status1('executed_migration_files','Jarmigration','upgrade')
        else:
            help_fun()
    else:
        help_fun()
        print ("Invalid command in db import please verify the help function")
   except KeyboardInterrupt:
        print ('done')
        print (termcolor.colored('Keyboard Interrupt ','red'))
        lggr.error('Keyboard Interrupt')
        sys.exit(1)
