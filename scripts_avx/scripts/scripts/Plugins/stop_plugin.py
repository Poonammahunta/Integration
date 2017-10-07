#!/usr/bin/python
import os
import sys
sys.path.insert(0, '../Commons/')
import avx_commons
import using_fabric
import termcolor
import set_path
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('PLUGINS')
import avx_commons
import signal
from termcolor import colored
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
class PluginStop():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the plugin stop operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def stop(self, plugin_specified, plugin_ips, plugin_ports, ip_execution):
        for each_plugin in plugin_specified:
            lggr.debug("Stoping Plugin (%s)" % each_plugin)
            if len(plugin_ips) == 0:
                plugin_ips = self.conf_data['PLUGINS'][each_plugin.lower()][
                    'ips']
                plugin_ports = self.conf_data['PLUGINS'][each_plugin.lower()][
                    'ports']
            index = self.conf_data['PLUGINS']['plugins'].index(each_plugin)
            try:
                vm_type,parameter = avx_commons.jar_name(each_plugin)
            except Exception:
                continue
            plugin_nodes = zip(plugin_ips, plugin_ports)
            for ip, port in plugin_nodes:
                lggr.debug('%s plugin starting in ip : %s' % (each_plugin,ip))
                if ip_execution and not self.user_input[0] == ip:
                    continue
                try:
                    username , path = avx_commons.get_username_path(self.conf_data, ip)
                    lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
                except Exception:
                    lggr.error("Error in getting username and path for %s" % ip)
                    print(colored("Error in getting username and path for %s" %ip,"red"))
                    continue
                lggr.debug('username and path for ip : %s is (%s,%s)' % (ip,username,path))
                command = using_fabric.AppviewxShell([ip], user=username)
                cmd = path + '/Python/bin/python ' + path + '/scripts/Plugins/plugin_stop.py ' + each_plugin + ' ' + port
                lggr.debug('Calling script to stop plugins : %s' % cmd)
                try:
                  l = command.run(cmd)
                except Exception:
                  print (colored('Error in communicating with %s' % ip,'red'))
                  continue
                lggr.debug('Result of plugin %s started in ip (%s): %s' % (each_plugin,ip,l))
                print_statement(each_plugin, '', ip, port, 'stopped')
            lggr.debug('%s plugin started in ip : %s' % (each_plugin,ip))
            plugin_ips = list()

