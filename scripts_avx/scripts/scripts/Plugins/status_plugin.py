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
import requests
from avx_commons import print_statement
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(current_file_path + '/../Mongodb'))
sys.path.insert(0, os.path.abspath(current_file_path + '/../Commons'))
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
class PluginStatus():

    def __init__(self, user_input, conf_data):
        self.user_input = user_input
        self.conf_data = conf_data

    def process_status(self,req_page,response_data=False):
        """."""
        try:
            response = requests.get(req_page,timeout=int(self.conf_data['GATEWAY']['gateway_timeout'][0]),verify=False)
            if response.status_code == 200:
                response_code="pageUp"
            else:
                response_code="pageDown"
            if response_data:
               return response_code,response
            return response_code
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception:
            if response_data:
               return "pageDown",''
            return "pageDown"

    def status(self,plugin_specified,plugin_ips,plugin_ports,ip_execution):
        plugin_data = True
        result= 'open'
        status_success = False
        for host in self.conf_data['GATEWAY']['hosts']:
            ip, port = host.split(':')
            result  = avx_commons.port_status(ip,port)
            if result == 'listening':
             if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
               http = 'https://'
             else:
               http = 'http://'
             url = http + host  + '/avxmgr/vmstatus'
             response,url_response = avx_commons.process_status(url,True)
             if response.lower() == 'pageup':
               status_success = True
               status_data = url_response.json()
               break
        for each_plugin in plugin_specified:
            if len(each_plugin) > 18:
                each_plugin_name = each_plugin[:15] + '...'
            else:
                each_plugin_name = each_plugin
            plugin_version = avx_commons.get_plugin_version(each_plugin)
            if len(plugin_ips) == 0:
                plugin_data = False
                try:
                    plugin_ips = self.conf_data['PLUGINS'][each_plugin.lower()][
                        'ips']
                    plugin_ports = self.conf_data['PLUGINS'][each_plugin.lower()][
                        'ports']
                except:
                    continue
            container_id_success = True
            try:
                container_id= avx_commons.jar_name(each_plugin,True)
            except Exception:
                container_id_success =False
            plugin_nodes = zip(plugin_ips, plugin_ports)

            for ip, port in plugin_nodes:
                if ip_execution and not self.user_input[0] == ip:
                    continue
                datacenter = avx_commons.get_datacenter(self.conf_data,ip)
                try:
                    if not status_success or not container_id_success:
                       raise Exception
                    url_response = status_data[container_id][datacenter][ip + ':' + port]
                except Exception:
                    url_response = 'not running'
                if url_response.lower() == 'running':
                    print_statement(each_plugin_name, plugin_version, ip, port, 'Running')
                else:
                    response = avx_commons.port_status(ip, port)
                    if response.lower() == 'listening':
                        print_statement(each_plugin, plugin_version, ip, port, 'running', 'not accessible')
                    else:
                        print_statement(each_plugin_name, plugin_version, ip, port, 'Not Running')
            if not plugin_data:
                plugin_ips = []
                plugin_ports = []

 
