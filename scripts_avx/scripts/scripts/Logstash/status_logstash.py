#!/usr/bin/python
import os
import sys
import avx_commons
import using_fabric
from termcolor import colored
import logger
lggr = logger.avx_logger('logstash')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import status_mongodb
import set_path
from avx_commons import print_statement
avx_path = set_path.AVXComponentPathSetting()

def print_statement(name, ip, port, comp_status=None):
        if comp_status.lower() == 'running':
            color = 'green'
        elif comp_status.lower() == 'not accessible':
            color = 'yellow'
        else:
            color = 'red'
        name = "[VIP]"
        print(
            '{0:6s} {1:31s}  {2:19s}  {3:10s} {4:5s}'.format(
                'logstash', colored(
                    name, "blue"), ip, port, colored(
                    comp_status, color)))

class LogstashStatus():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the logstash status operation : [%s]' % user_input)
        self.conf_data = conf_data
        self.user_input = user_input
        self.gate_version = 'v' + self.conf_data['COMMONS']['version'][0]
        self.logstash_version = 'v' + self.conf_data['COMMONS']['version'][0]

    def status(self, logstash_nodes,mute=False):
        return_status = False
        for ip, port in logstash_nodes:
            lggr.debug('Checking logstash status for ip (%s)' % ip)
            try:
                username, path = avx_commons.get_username_path(
                    self.conf_data, ip)
                lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
            port_check = avx_commons.port_status(ip,int(port))
            syslog_port = avx_commons.udp_port_status(self.conf_data['LOGSTASH']['syslog_vip_host'][0],self.conf_data['LOGSTASH']['syslog_vip_port'][0])
            if port_check == 'listening':
               if syslog_port =='listening':
                  avx_commons.print_statement('avx_platform_logs',self.logstash_version,ip, port, 'Running') 
               else:
                  avx_commons.print_statement('avx_platform_logs',self.logstash_version,ip, port, 'Not Accessible')
            else:
               avx_commons.print_statement('avx_platform_logs',self.logstash_version,ip, port, 'Not Running')

    def logstash_vip_status(self,mute = False):
       if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'true':
         if self.conf_data['LOGSTASH']['vip_enabled'][0].lower() == 'true':
          try:
            ip,port = self.conf_data['LOGSTASH']['vip_host'][0].split(':')
          except:
                print (colored('APPVIEWX_logstash_VIP(%s) - (IP format) under logstash section is not valid' % self.conf_data['logstash']['appviewx_logstash_vip'][0],'red'))
          port_check= avx_commons.port_status(ip,port)
          if port_check.lower() == 'listening':
                        print_statement('avx_platform_logs',self.logstash_version,ip, port, 'Running', self.gate_version)
          else:
                        print_statement('avx_platform_logs',self.logstash_version,ip, port, 'Not Running', self.gate_version)


