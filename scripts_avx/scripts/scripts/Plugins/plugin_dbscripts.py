"""The script to execute the plugin related db scripts."""
import os
import sys
import json
import signal
import socket
import logger
import subprocess
import avx_commons
from config_parser import config_parser
lggr = logger.avx_logger('plugin_dbscripts')
hostname = socket.gethostbyname(socket.gethostname())
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_location = os.path.dirname(os.path.realpath(__file__))


class PluginScripts():
    """The class to execute the plugin related db scripts."""

    """The script looks for db scripts in each plugin directory. If
    scripts are found in the directory, then they are executed and
    details stored in the db. If a script/jar is already executed, then it is
    not executed again."""

    def __init__(self):
        """Define the class variables."""
        conf_file = os.path.abspath(
            current_file_location + '/../../conf/appviewx.conf')
        self.conf_data = config_parser(conf_file)
        self.path = self.conf_data['ENVIRONMENT']['path'][
            self.conf_data['ENVIRONMENT']['ips'].index(hostname)]
        self.cmd_list = dict()
        self.files = list()

    def set_env_variables(self):
        """Function to set the mongo and jre related variables."""
        try:
            primary_db = avx_commons.primary_db(self.conf_data, status=True)
        except:
            lggr.error('Unable to fetch primary db details. ' +
                       'So coudnt execute plugin related db scripts.')
            sys.exit(1)

        self.mongo_ip, self.mongo_port = primary_db.split(':')
        self.db_username, self.db_password, self.db_name = \
            avx_commons.get_db_credentials()
        self.java_path = self.path + '/jre/bin/java'
        self.mongo_path = self.path + '/db/mongodb/bin/mongo'

    def execute_cmd(self):
        """Execute all the commands in the commands list."""
        for cmd, name in self.cmd_list.items():
            lggr.debug('Exceuting command: ' +
                       cmd.replace('-p ' + self.db_password, '-p xxxxxxxx'))
            ps = subprocess.run(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            if ps.returncode:
                lggr.error('Error in executing command: ' +
                           cmd.replace(
                               '-p ' + self.db_password, '-p xxxxxxxx'))
                lggr.error('Error: ' + ps.stdout.decode() +
                           '\n' + ps.stderr.decode())
                try:
                    self.files.remove(name)
                except:
                    lggr.error('Unable to execute: ' + name)

    def get_mongo_client_instance(self):
        """Function will get the details of mongo and return a mongo object."""
        collection_name = 'system_files_executed'
        try:
            db_ob = avx_commons.db_connection(self.conf_data, status=True)
        except:
            print('Unable to connect to db!!')
            sys.exit(1)

        plugin_data_ob = db_ob['appviewx'][collection_name].find()
        found = False
        for plugin_data in plugin_data_ob:
            if plugin_data["_id"] == "executed_plugin_scripts":
                found = True
                break
        if not found:
            plugin_data = {"_id": "executed_plugin_scripts", "files": []}
        self.files_already_executed = plugin_data['files']

    def update_info_in_db(self):
        """Update db with the executed plugin scripts details."""
        cmd_to_update_db = self.mongo_path + ' ' + self.mongo_ip + ':' +\
            str(self.mongo_port) + '/appviewx -u ' + self.db_username +\
            ' -p ' + self.db_password + ' --authenticationDatabase ' +\
            self.db_name + ' --quiet ' + current_file_location +\
            '/.plugin_scripts.js'
        subprocess.Popen(cmd_to_update_db, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_execution_cmds(self, location, plugin_name, version):
        """Generate the command for execution of db scripts."""
        cwd = os.getcwd()
        os.chdir(location)
        for dir in os.listdir(location):
            file_name = plugin_name + '_' + version + '_' + dir
            if file_name in self.files_already_executed:
                self.files.append(file_name)
                continue
            dir = os.path.abspath(dir)
            if os.path.isdir(dir):
                self.get_execution_cmds(dir, plugin_name, version)
            else:
                if dir.endswith('.js'):
                    self.cmd_list[self.mongo_path + ' ' +
                                  self.mongo_ip + ':' +
                                  str(self.mongo_port) + '/appviewx ' +
                                  '-u ' + self.db_username + ' -p ' +
                                  self.db_password +
                                  ' --authenticationDatabase ' +
                                  self.db_name + ' --quiet ' +
                                  os.path.abspath(dir)] = file_name
                    self.files.append(file_name)
                elif dir.endswith('.jar'):
                    if 'StoreHelperScripts.jar'.lower() in dir.lower():
                        self.cmd_list[self.java_path +
                                      ' -Dappviewx.property.path=' +
                                      self.path + '/properties -jar ' +
                                      os.path.abspath(dir) + ' ' + self.path +
                                      '/aps/defaultHelperScripts/'] = file_name
                    else:
                        self.cmd_list[self.java_path + ' -jar' +
                                      ' ' + os.path.abspath(dir) +
                                      ' ' + self.path +
                                      '/properties/'
                                      ] = file_name
                    self.files.append(file_name)
        os.chdir(cwd)

    def execute_db_scripts(self):
        """Function to execute the db scripts."""
        plugin_dir = self.path + '/Plugins'
        enabled_plugins = self.conf_data['PLUGINS']['plugins']
        out_content = {}
        out_content['_id'] = 'executed_plugin_scripts'
        out_content['files'] = list()
        for plugin in enabled_plugins:
            individual_plugin_path = os.path.abspath(
                plugin_dir + '/' + plugin)
            if not os.path.exists(individual_plugin_path):
                print('Path not found: ' + individual_plugin_path)
                lggr.error('Path not found: ' + individual_plugin_path)
                continue

            for dir in sorted(os.listdir(individual_plugin_path)):
                abs_dir = individual_plugin_path + '/' + dir
                if dir.startswith('Release') and os.path.isdir(abs_dir):
                    self.get_execution_cmds(
                        abs_dir, plugin, dir.split('_')[-1])
        out_file = open(current_file_location + '/.plugin_scripts.js', 'w+')
        self.execute_cmd()
        out_content['files'] = self.files
        out_file.write(
            'db.system_files_executed.save(' + json.dumps(out_content) + ')')

    def initialize(self):
        """Initialize."""
        if not os.path.exists(self.path + '/Plugins'):
            print('Plugin directory not found at ' + os.path.abspath(
                self.path + '/Plugins'))
            sys.exit(1)
        self.set_env_variables()
        self.get_mongo_client_instance()
        self.execute_db_scripts()
        self.update_info_in_db()


if __name__ == '__main__':
    ob = PluginScripts()
    ob.initialize()
