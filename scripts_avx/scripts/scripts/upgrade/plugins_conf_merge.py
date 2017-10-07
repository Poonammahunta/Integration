import os 
import sys
import subprocess
import json 
import logging
import configparser
from configobj import ConfigObj
import glob

def either(c):
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c


class Merge_configuration_file():
    
    def __init__(self):
        a = 'init_function'

    def current_file(self):
        
        '''This function is to get the current file name'''
        current_file = inspect.getfile(inspect.currentframe())
        return current_file
    
    def current_frame(self):
        
        '''This function can be used to get the current directory in which the script is running'''
        current_directory = os.path.dirname(os.path.realpath(__file__))
        return current_directory
    
    def Execute_command(self,command):
        try:
            ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()
        except Exception as e:
            print (e)
            print ("Error in executing the command" + output )
            sys.exit(1)
        return output

    def list_directory(self,location):

        if not os.path.exists(location):
            return None
        else:
            return os.listdir(location)


    def get_AppViewX_location(self):

        '''This function returns location where AppViewX is installed'''
        current_location = self.current_frame()
        AppViewX_location = current_location.split('/scripts')[0]
        return AppViewX_location  

    def verify_location(self,location,directory=None):

        '''This functin verifies if a given directory is present in the location'''
        if directory:
            return os.path.exists(location + '/' + directory)
        else:
            return os.path.exists(location)

    def copy_files(self,source_location,target_location,quit=None):

        if not os.path.exists(source_location):
            print ("The location " + source_location + " is not available")
            command = "cp " + source_location + ' ' + target_location
            print (command) 

    def get_base_plugins_location(self):

        try:
            plugins_location = self.current_frame() + '/../../Plugins/'
            if plugins_location:
                return plugins_location
            else:
                return None
        except Exception as e:
            print (e)
            sys.exit(1)

    def get_plugins_conf(self,location,plugin):

        try:

            plugins_conf_location = glob.glob(''.join(map(either, location + '/' + plugin + '/*.conf')))[0]
            print (plugins_conf_location)
            if plugins_conf_location:
                return plugins_conf_location
        except Exception as e:
            print (e)
            sys.exit(1)

    def get_advanced_plugins_location(self):
        
        try:
            plugins_location = self.current_frame() + '/../../patch/AppViewX_Patch/Plugins/'
            if plugins_location:
                return plugins_location
            else:
                return None    
        except Exception as e:
            sys.exit(1)


    def backup_plugins_conf_file(self):
        
        AppViewX_location = self.get_AppViewX_location()
        plugins_location =  self.get_base_plugins_location()
        plugins = self.list_directory(plugins_location)
        for plugin in plugins:
            if 'BUILDINFO' == plugin.upper():
                plugins.remove(plugin)
        for plugin in plugins:
            source_location = self.get_plugins_conf(plugins_location,plugin)
            target_location = plugins_location + '/' + plugin + '/' + '/backup/'
            command  = "rsync -avz " +  source_location + ' ' + target_location
            print (command)
            os.system(command)

    def synchronize_advanced_plugins_conf(self):
        
        AppViewX_location = self.get_AppViewX_location()
        advanced_plugins_location =  self.get_advanced_plugins_location()
        advanced_plugins = self.list_directory(advanced_plugins_location)
        for plugin in advanced_plugins:
            if 'BUILDINFO' == plugin.upper():
                advanced_plugins.remove(plugin)
        base_plugins_location = self.get_base_plugins_location()
        base_plugins = self.list_directory(base_plugins_location)
        
        for plugin in advanced_plugins:
            if plugin in base_plugins:
                command  = "rsync -avz "  + (glob.glob(''.join(map(either, advanced_plugins_location + '/' + plugin + '/*.conf'))))[0]  + ' ' + base_plugins_location + '/'+ plugin + '/'
                print (command)
                os.system(command)
                backup_conf_location =  glob.glob(''.join(map(either,base_plugins_location + '/' + plugin + '/backup/' +'*.conf')))[0]
                advanced_conf_location = glob.glob(''.join(map(either, base_plugins_location + '/' + plugin + '/' + '/*.conf')))[0]
                self.Execute_command(command)
                if os.path.exists(backup_conf_location):
                    backup_config = ConfigObj(backup_conf_location)
                    advanced_config = ConfigObj(advanced_conf_location)
                    print (advanced_conf_location)
                    print (backup_conf_location)
                    advanced_config.write_empty_values=True
                    advanced_config.interpolate=False
                    backup_config.interpolate=False
                    advanced_config.merge(backup_config)
                    advanced_config.write()
            
            else:
                command  = "rsync -avz "  + (glob.glob(''.join(map(either, advanced_plugins_location + '/' + plugin + '/*.conf'))))[0]  + ' ' + base_plugins_location + '/'+ plugin + '/'
                os.system(command)

if __name__ == "__main__":

    Merge_configuration_file.backup_plugins_conf_file(Merge_configuration_file())
    Merge_configuration_file.synchronize_advanced_plugins_conf(Merge_configuration_file())