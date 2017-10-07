#!/usr/bin/python
import os
import sys
import avx_commons
import using_fabric
from termcolor import colored
import logger
lggr = logger.avx_logger('GATEWAY')
import avx_commons
import signal
from avx_commons import print_statement
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(current_file_path + '/../Mongodb'))
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class GatewayStatus():

    def __init__(self, user_input, conf_data):
        self.conf_data = conf_data
        self.user_input = user_input
        self.gate_version = 'v' + self.conf_data['COMMONS']['version'][0]

    def status(self, gateway_nodes,mute=False):
        self.gateway_vip_status(mute)
        return_status = False
        for ip, port in gateway_nodes:
            try:
                username, path = avx_commons.get_username_path(
                    self.conf_data, ip)
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
            url = "http://" + ip + ":" + port + '/avxmgr/api'
            try:
                if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
                    url = "https://" + ip + ":" + port + '/avxmgr/api'
            except Exception:
                pass
            url_response = avx_commons.process_status(url)
            if url_response.lower() == 'pageup':
               return_status = True
               if not mute:
                    print_statement('Gateway', self.gate_version, ip, port, 'Running')
            else:
                    response = avx_commons.port_status(ip, port)
                    if response.lower() == 'listening':
                       return_status = True
                       if not mute:
                        print_statement('Gateway', self.gate_version, ip, port, 'Not Accessible')
                    else:
                       if not mute:
                           print_statement('Gateway', self.gate_version, ip, port, 'Not Running')
        return return_status

    def gateway_vip_status(self,mute = False):
       if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'true':
         if self.conf_data['GATEWAY']['gateway_vip_enabled'][0].lower() == 'true':
          try:
            ip,port = self.conf_data['GATEWAY']['appviewx_gateway_vip'][0].split(':')
          except:
            if not mute:
                print (colored('APPVIEWX_GATEWAY_VIP(%s) - (IP format) under GATEWAY section is not valid' % self.conf_data['GATEWAY']['appviewx_gateway_vip'][0],'red'))
            return
          url = "http://" + ip + ":" + port + '/avxmgr/api'
          try:
                if self.conf_data['GATEWAY']['appviewx_gateway_vip_https'][0].lower() == 'true':
                    url = "https://" + ip + ":" + port + '/avxmgr/api'
          except Exception:
                pass
          url_response = avx_commons.process_status(url)
          if url_response.lower() == 'pageup':
                    if not mute:
                        print_statement('Gateway', self.gate_version, ip, port, 'Running','VIP')
          else:
                    response = avx_commons.port_status(ip, port)
                    if response.lower() == 'listening':
                        if not mute:
                            print_statement('Gateway', self.gate_version, ip, port, 'Not Accessible','VIP')
                    else:
                        if not mute:
                            print_statement('Gateway', self.gate_version, ip, port, 'Not Running','VIP')


