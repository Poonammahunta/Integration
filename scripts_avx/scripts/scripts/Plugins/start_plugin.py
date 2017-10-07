#!/usr/bin/python
import os
import sys
import avx_commons
import using_fabric
import set_path
from termcolor import colored
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('PLUGINS')
import avx_commons
import signal
import socket
from configobj import ConfigObj
from avx_commons import print_statement
localhost = socket.gethostbyname(socket.gethostname())
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))
class PluginStart():


    def __init__(self,user_input, conf_data):
        lggr.debug('User input for the plugin start operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data


    def start(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        scripts_conf = ConfigObj(current_file_path + '/../conf/script.conf')
        try:
          jmx_monitor = scripts_conf['JMX_MONITOR']
          jmx_port = int(scripts_conf['JMX_PORT_START'])
        except:
          jmx_monitor = 'False'
        for each_plugin in plugin_specified:
            
            lggr.debug("Starting Plugin (%s)" % each_plugin)
            try:
               heap_min = avx_commons.get_heap_size(each_plugin,'min')
            except Exception:
               try:
                   heap_min = self.conf_data['VM_CONF']['heap_min'][0]
               except Exception:
                   heap_min = '512m'
            try:
               heap_max = avx_commons.get_heap_size(each_plugin,'max')
            except Exception:
               heap_max = self.conf_data['VM_CONF']['heap_max'][0]
            except Exception:
               heap_max = '1024m'
            index = self.conf_data['PLUGINS']['plugins'].index(each_plugin)
            if len(plugin_ips) == 0:
               try:
                plugin_ips = self.conf_data['PLUGINS'][each_plugin.lower()]['ips']
                plugin_ports = self.conf_data['PLUGINS'][each_plugin.lower()]['ports']
               except KeyError:
                plugin_ips = list()
                print(colored("<IP:PORT> details for plugin (%s) is not configured in conf file" %  each_plugin,"red"))
                continue
            if len(plugin_ips) == 0:
                continue

            plugin_nodes = zip(plugin_ips,plugin_ports)
            try:
                vm_type,parameter = avx_commons.jar_name(each_plugin)
                parameter = parameter.replace(':','=')
            except Exception as e:
                plugin_ips =list()
                continue
            if vm_type.lower() == 'northbound':
                framework_jar='framework-db.jar'
            elif vm_type.lower() == 'southbound':
                framework_jar='framework-core.jar'
            else:
                lggr.error("CATEGORY field in %s conf file should be either northbound or southbound" %each_plugin)
                print(colored("CATEGORY field in %s conf file should be either northbound or southbound" %each_plugin,"red"))
                continue
            for ip,port in plugin_nodes:
                lggr.debug('%s plugin starting in ip : %s' % (each_plugin,ip))
                if ip_execution and not self.user_input[0] == ip:
                    continue
                try:
                    datacenter = avx_commons.get_datacenter(self.conf_data, ip)
                    lggr.debug('Datacenter for ip(%s) : %s' % (ip,datacenter))
                except Exception:
                    lggr.error("Error in getting datacenter for %s" % ip)
                    print(colored("Error in getting datacenter for ip %s from conf file" %ip,"red"))
                    continue
                try:
                    username , path = avx_commons.get_username_path(self.conf_data, ip)
                    lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
                except Exception:
                    lggr.error("Error in getting username and path for %s" % ip)
                    print(colored("Error in getting username and path for %s" %ip,"red"))
                    continue
                lggr.debug('username and path for ip : %s is (%s,%s)' % (ip,username,path))
                parameter = parameter.replace('{AVX_HOME}',path)
                port_status = avx_commons.port_status(ip,port)
                if port_status == 'listening':
                   print_statement(each_plugin, '', ip, port, 'running')
                   continue
                command = using_fabric.AppviewxShell([ip],user=username,pty=False)
                if ip == localhost and not os.path.isfile(path + '/Plugins/framework/' + framework_jar):
                  print(colored('framework jar not found at ' + path + '/Plugins/framework/' + framework_jar, 'red'))
                  print_statement(each_plugin, '', ip, port, 'not started')
                  continue
                if jmx_monitor.lower() == 'true':
                    jmx_port = jmx_port + 1
                    cmd = 'nohup ' + path + '/jre/bin/java -Xms' + str(heap_min) + ' -Xmx' + str(heap_max) + ' -XX:PermSize=64M -XX:MaxPermSize=512M -cp '+ path  + '/Plugins/' + each_plugin + "/" +  each_plugin + '.jar:' + path + '/Plugins/framework/' + framework_jar + ':' + path + '/properties -Ddatacenter=' + datacenter + ' -Davx_logs_home=' + path + '/logs/' + each_plugin + '/  -Davx_property_file_path=' + path + '/properties/appviewx.properties' +" -Dlog4j.configuration=file:" + path +"/Plugins/" + each_plugin+"/log4j." + each_plugin + ' -Dport=' + port  +  ' -Dgzip=true -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=' + str(jmx_port) + ' -Dcom.sun.management.jmxremote.local.only=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false ' + parameter + ' com.appviewx.common.framework.jetty.Main > ' +  path + '/logs/'  + each_plugin +'_start.log 2>&1 &'
                else:
                    cmd = 'nohup ' + path + '/jre/bin/java -Xms' + str(heap_min) + ' -Xmx' + str(heap_max) + ' -XX:PermSize=64M -XX:MaxPermSize=512M -cp '+ path  + '/Plugins/' + each_plugin + "/" +  each_plugin + '.jar:' + path + '/Plugins/framework/' + framework_jar +':' + path + '/properties -Ddatacenter=' + datacenter + ' -Davx_logs_home=' + path + '/logs/' + each_plugin + '/  -Davx_property_file_path=' + path + '/properties/appviewx.properties' +" -Dlog4j.configuration=file:" + path +"/Plugins/" + each_plugin+"/log4j." + each_plugin + ' -Dport=' + port  +  ' -Dgzip=true ' + parameter + ' com.appviewx.common.framework.jetty.Main > ' +  path + '/logs/'  + each_plugin +'_start.log 2>&1 &'
                if avx_commons.port_status == 'listening':
                   print_statement(each_plugin, '', ip, port, 'running')
                   continue
                lggr.debug('Command to start plugin (%s) : %s' % (each_plugin,cmd))
                try:
                   l = command.run(cmd)
                except Exception:
                   print (colored('Error in communicating with %s' % ip,'red'))
                   continue
                lggr.debug('Result of plugin %s started in ip (%s): %s' % (each_plugin,ip,l))
                if list(l[1])[0][1]:
                   print_statement(each_plugin, '', ip, port, 'starting')
                else:
                    print_statement(each_plugin, '', ip, port, 'not started')
            lggr.debug('%s plugin started in ip : %s' % (each_plugin,ip))
            plugin_ips = list()


