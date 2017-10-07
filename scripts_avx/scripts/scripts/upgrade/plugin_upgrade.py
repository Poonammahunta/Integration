import os 
import sys
from get_dependencies import Get_dependencies
if not os.path.realpath('Commons/') in sys.path:
    sys.path.append(os.path.realpath('Commons/'))
current_directory = os.path.dirname(os.path.realpath(__file__))
from dependency_check import dependency_check
import configparser
from config_parser import config_parser
conf_data = config_parser(current_directory + '/../../conf/appviewx.conf')
config = configparser.SafeConfigParser()
config.optionxform  =str
config.read(current_directory + '/../../conf/appviewx.conf')
import subprocess
sys.path.insert(0, current_directory + '/../Commons')
class Plugin_upgrade():
    
    def __init__(self):
        
        #patch_location = self.patch_location
        pass

    def valiadte_file_location(self,file_location):
        if os.path.exists(file_location):
            return True
        else:
            return False
    
    def get_plugins(self,location):
        plugins = os.listdir(location)
        return plugins

    def extract_file(self,file_location,target_location):
        command = "tar -xvf " + file_location + ' -C ' + target_location
        ps = self.run_local_cmd(command)
        return ps

    def add_entry_in_conf_file(self,new_plugin):
        with open('../conf/appviewx.conf','r') as in_file:
            content = in_file.readlines()
        enabled_plugins = conf_data['PLUGINS']['plugins']
        plugin_index = dict()
        plugin_ips = list()
        for ip in conf_data['ENVIRONMENT']['ips']:
            plugin_ports = list()
            for plugin in enabled_plugins:
                if ip in conf_data['PLUGINS'][plugin]['ips']:
                    if ip not in plugin_ips:
                        plugin_ips.append(ip)
                    plugin_ports.append(int(conf_data['PLUGINS'][plugin]['ports'][conf_data['PLUGINS'][plugin]['ips'].index(ip)]))
            plugin_ports = sorted(plugin_ports,key=int)
            plugin_index[ip] = plugin_ports
        if len(plugin_ips) == 1:
            config.set('PLUGINS',new_plugin,plugin_ips[0] + ':' + str(plugin_index[plugin_ips[0]][-1]+1))
        else:
            config.set('PLUGINS',plugin_ips[-1] + ':'+ str(plugin_index[plugin_ips[-1]][-1]+1))
            config.set('PLUGINS',new_plugin,plugin_ips[-2] + ':' + str(plugin_index[plugin_ips[-2]][-1]+1))
            print(plugin_index[plugin_ips[-1]][-1]+1)
            print (plugin_index[plugin_ips[-2]][-1]+1)
        new_conf_file = current_directory + '/../../conf/appviewx.conf'
        with open(new_conf_file,'w') as out_file:
            config.write(out_file)
        # f = open(new_conf_file).readlines()
        # lis = []
        # location = None
        # for line in f:
        #     try:
        #         key, b = map(str.strip, line.split("="))
        #         lis.append(" = ".join([key, str(config.get(location, key))]) + "\n")
        #     except:
        #         if line.startswith("["):
        #             location = line[1:len(line)-2]
        #             lis.append("\n"+line)
        #         elif line.startswith("#"):
        #             lis.append(line)
        # g =open(new_conf_file, 'w')
        # g.writelines(lis)
        # for line in content:
        #   if 'ENABLED_PLUGINS' in line:
        #       plugin_components = conf_data[]
        #       if conf_data['ENVIRONMENT']['multinode'][0].upper() == 'FALSE':
        #           config.set('PLUGINS',plugin,str(port_number))
        #       else:
        #           config.set(conf_data['ENVIRONMENT']['ips'][-1],plugin,str(port_number+30))
        #           config.set(conf_data['ENVIRONMNET']['ips'][-2],plugin,str(port_number+30))
    def run_local_cmd(self,cmd):
        """The function is used to execute a shell command."""
        try:
            ps = subprocess.run(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            ret_code = ps.returncode
            out = ps.stdout.decode()
            err = ps.stderr.decode()
            return ps
        except Exception as e:
            print(e)
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
    def patch_plugins(self,source_location,target_location,plugin):
        base_plugins = os.listdir(source_location)
        advanced_plugins = os.listdir(target_location)
        if plugin in base_plugins:
            #cmd =  'mkdir -p ' + source_location + '/' + plugin + '/backup'
            #ps = run_local_cmd(cmd)
            cmd = 'rm -rf ' + source_location + '/' + plugin + '/backup/'
            ps = self.run_local_cmd(cmd)
            cmd =  'rsync -avz  ' + source_location + '/' + plugin + '/* '  + source_location + '/' + plugin + '/backup/' 
            ps = self.run_local_cmd(cmd)
            #cmd = current_directory + '/../../Python/bin/python ' + current_directory + '/plugin_conf_merge.py'
            #ps  = run_local_cmd(cmd)
            # cmd = "rm -rf  " + target_location + '/' + plugin+ '/*.jar ' + source_location + '/' + source_location + '/release_scripts  ' + source_location + '/' + plugin+ '/log4j* ' + source_location + '/' + plugin+ '/*.conf '
            # ps = self.run_local_cmd(cmd)
            # cmd =  'cp -r ' + target_location + '/' + plugin + '*.jar ' + target_location + '/' + plugin + 'release_scripts ' + target_location + '/' + plugin + 'log4j* ' + target_location + '/' + plugin + '*.conf '+ source_location + '/' + plugin + '/.'
            # print (cmd)
            cmd = "rsync -avz " + target_location + '/' + plugin + '/' + plugin + '.jar ' + source_location+ '/' + plugin + '/' + plugin + '.jar ' 
            ps = self.run_local_cmd(cmd)
            cmd = "rsync -avz " + target_location + '/' + plugin + '/' + plugin + '.conf ' + source_location+ '/' + plugin + '/' + plugin + '.conf '
            ps = self.run_local_cmd(cmd)
            cmd = "rsync -avz " + target_location + '/' + plugin + '/' + plugin + '_dependencies ' + source_location+ '/' + plugin + '/' + plugin + '.dependencies '
            ps = self.run_local_cmd(cmd)

        else:
            cmd = 'cp -r ' + target_location + '/' + plugin  + ' ' + source_location + '/'
            ps = self.run_local_cmd(cmd)
            # self.add_entry_in_conf_file(plugin)

    def upgrade_plugin(self):
        patch_location = sys.argv[1]
        if self.valiadte_file_location(patch_location):
            patch_target_location = current_directory + '/../../patch/AppViewX_Patch/'
            ps = self.run_local_cmd('mkdir -p ' + patch_target_location)
            ps = self.run_local_cmd('rm -rf ' + patch_target_location + '/*')
            ps = self.extract_file(patch_location,patch_target_location + '.')
            advanced_plugin_path = patch_target_location + '/Plugins/'
            plugins = self.get_plugins(advanced_plugin_path)
            for plugin in plugins:
                plugin_dependency_location = advanced_plugin_path + '/' + plugin + '/' + plugin + '_dependencies'
                if self.valiadte_file_location(plugin_dependency_location):
                    dependency_data = Get_dependencies.obtain_plugin_dependencies(Get_dependencies(),plugin_dependency_location)
                    dependency_result = dependency_check(dependency_data)
                    source_location = current_directory + '/../../Plugins/'
                    target_location = current_directory + '/../../patch/AppViewX_Patch/Plugins/'
                    if len(dependency_result) == 0:
                        self.patch_plugins(source_location,target_location,plugin)
                    else:
                        return "The dependencies has not been matched please do resolve it."
                        
                else:
                    source_location = current_directory + '/../../Plugins/'
                    target_location = current_directory + '/../../patch/AppViewX_Patch/Plugins/'
                    self.patch_plugins(source_location,target_location,plugin)
if __name__ == "__main__":
	Plugin_upgrade.upgrade_plugin(Plugin_upgrade())