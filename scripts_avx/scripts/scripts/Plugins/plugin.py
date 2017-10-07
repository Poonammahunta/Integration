#!../Python/bin/python
""" Common class to perform the mainpulation of plugin operations"""
import sys
import avx_commons
import start_plugin
import status_plugin
import stop_plugin
import logger
import os
import time
from termcolor import colored
env_path=os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(os.path.realpath(os.path.join(env_path , '../')))		
from status import status		
s = status()
lggr = logger.avx_logger('PLUGINS')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import monitorconfigure
def help_fun(operation):
        print(" ERROR in user_input:")
        print(" \t\t 1) ./appviewx %s plugins" % operation)
        print (" \t\t 2) ./appviewx %s plugins <plugin_name>" % operation)
        print(
            " \t\t 3) ./appviewx %s plugins <plugin_name> <ip>" % operation)
        print(
            " \t\t 4) ./appviewx %s plugins <plugin_name> <ip> <port>" % operation)
        sys.exit(1)

def reload_help_fun():
        print(" ERROR in user_input:")
        print(" \t\t 1) ./appviewx --gwrefresh" % operation)
        sys.exit(1)

class Plugin():

    def __init__(self, user_input, conf_data):
        lggr.debug("User input for plugin operation: %s" % user_input)
        lggr.info("User input for plugin operation: %s" % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def gw_reload(self):
        http='http'
        time.sleep(2)
        import subprocess
        for host in self.conf_data['GATEWAY']['hosts']:
            if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
               http = 'https'
            ip,port = host.split(':')
            checking_status_cmd = 'cd ' + env_path + '../&& ./appviewx --status gateway ' + ip
            status_value = subprocess.run(checking_status_cmd, shell=True,
                                          stdout=subprocess.PIPE).stdout.decode()
            url = http + '://' + ip + ':' + port + '/avxmgr/refresh'
            if not 'Not Running' in status_value:
             response = avx_commons.process_status(url)
             if response == "pageUp":
               print (colored('Gateway successfully reloaded @ ' + ip,"green"))
             else:
               print (colored('Gateway failed to reload @ ' + ip,"red"))


    def plugin_start(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        # print (plugin_specified)
        lggr.debug("Redirect to the plugins start operation")
        lggr.info("Redirect to the plugins start operation")
        obj = start_plugin.PluginStart(self.user_input[2:], self.conf_data)
        obj.start(plugin_specified,plugin_ips,plugin_ports,ip_execution)

    def plugin_stop(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        lggr.debug("Redirect to the plugins stop operation")
        lggr.info("Redirect to the plugins stop operation")
        obj = stop_plugin.PluginStop(self.user_input[2:], self.conf_data)
        obj.stop(plugin_specified,plugin_ips,plugin_ports,ip_execution)
     
    def plugin_restart(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        lggr.debug("Redirect to the plugins restart operation")
        lggr.info("Redirect to the plugins restart operation")
        obj = stop_plugin.PluginStop(self.user_input[2:],self.conf_data)
        obj.stop(plugin_specified,plugin_ips,plugin_ports,ip_execution)
        obj = start_plugin.PluginStart(self.user_input[2:],self.conf_data)
        obj.start(plugin_specified,plugin_ips,plugin_ports,ip_execution)

    def plugin_status(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        lggr.debug("Redirect to the plugins status operation")
        lggr.info("Redirect to the plugins status operation")
        obj = status_plugin.PluginStatus(self.user_input[2:], self.conf_data)
        obj.status(plugin_specified,plugin_ips,plugin_ports,ip_execution)

    def operation(self):
        if self.user_input[0] in ['--start','--stop','--status','--restart']:
           lggr.debug("User input for plugin start operation" % self.user_input)
           lggr.info("User input for plugin start operation" % self.user_input)
           if len(self.user_input) > 5:
              help_fun(self.user_input[0])
           if len(self.user_input) <= 2:
              self.user_input.append('all')
           ip_execution = False
           enabled_plugins = self.conf_data['PLUGINS']['plugins']
           plugin_ips = list()
           plugin_ports = list()
           if self.user_input[2] == 'all':
              if len(self.user_input) > 3:
                  help_fun(self.user_input[0])
              plugin_specified = enabled_plugins
           elif self.user_input[2].lower() in enabled_plugins:
              self.user_input[2] = self.user_input[2].lower()
              plugin_specified = [self.user_input[2]]
              plugin_name = self.user_input[2]
              if len(self.user_input) == 4:
                try:
                 plugin_ips =[]
                 plugin_ports =[]
                 if self.user_input[3] in self.conf_data['PLUGINS'][plugin_name.lower()]['ips']:
                    for index in range(0,len(self.conf_data['PLUGINS'][plugin_name.lower()]['ips'])):
                        if self.user_input[3] == self.conf_data['PLUGINS'][plugin_name.lower()]['ips'][index]:
                            plugin_ips.append(self.user_input[3])
                            plugin_ports.append(self.conf_data['PLUGINS'][plugin_name.lower()]['ports'][index])
                 else:
                    help_fun(self.user_input[0])
                except KeyError:
                 print(colored("<IP:PORT> details for plugin (%s) is not configured in conf file" %  each_plugin,"red"))
                 sys.exit(1)
              elif len(self.user_input) == 5:
               try:
                if self.user_input[3] + ":" + self.user_input[4] in self.conf_data['PLUGINS'][plugin_name.lower()]['hosts']:
                   plugin_ips =  [self.user_input[3]]
                   plugin_ports = [self.user_input[4]]
                else:
                    help_fun(self.user_input[0])
               except KeyError:
                print(colored("<IP:PORT> details for plugin (%s) is not configured in conf file" %  each_plugin,"red"))
                sys.exit(1)
           elif self.user_input[2] in self.conf_data['ENVIRONMENT']['ips']:
            if len(self.user_input) > 3:
               help_fun(self.user_input[0])
            ip_execution = True
            plugin_specified = enabled_plugins
           else:
               help_fun(self.user_input[0])
           lggr.debug("Finding the operation of plugins(Start/Stop/Restart/Status)")
           if self.user_input[0].lower() == '--start':
              self.plugin_start(plugin_specified,plugin_ips,plugin_ports,ip_execution)
           elif self.user_input[0].lower() == '--stop':
              self.plugin_stop(plugin_specified,plugin_ips,plugin_ports,ip_execution)
           elif self.user_input[0].lower() == '--status':
              self.plugin_status(plugin_specified,plugin_ips,plugin_ports,ip_execution)
           elif self.user_input[0].lower() == '--restart':
               self.plugin_restart(plugin_specified,plugin_ips,plugin_ports,ip_execution)
           #if self.user_input[0].lower() == '--restart' or self.user_input[0].lower() == '--start':
           #    self.gw_reload()
        else:
            lggr.error("The PLUGINS command supports only basic actions (start, stop, restart,stop)")
            lggr.error("User_input is not valid: %s " % self.user_input)
            help_fun('--start/--stop/--restart/--status')
