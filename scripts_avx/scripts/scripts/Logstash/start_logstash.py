#!/usr/bin/python
import os
import sys
import avx_commons
import using_fabric
import set_path
import socket
from termcolor import colored
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_path + '/../Commons')
hostname = socket.gethostbyname(socket.gethostname())
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('LOGSTASH')
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class LogstashStart():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the logstash start operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def start(self, logstash_nodes):
        for ip, port in logstash_nodes:
            lggr.debug('Starting logstash in %s' % ip)
            try:
                username, path = avx_commons.get_username_path(
                    self.conf_data, ip)
                lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
            except Exception:
                print("Error in getting username and path for %s" % ip)
            lggr.debug('username and path for ip (%s): [%s,%s]' % (ip, username, path))
            try:
                datacenter = avx_commons.get_datacenter(self.conf_data, ip)
            except Exception as e:
                lggr.error("Error in getting username and path for %s" % ip)
                print(e)
                print(
                    colored(
                        "Error in getting datacenter for ip %s from conf file" %
                        ip, "red"))
                continue
            lggr.debug('Datacenter assigned for ip (%s): %s' % (ip, datacenter))
            logstash_directory = avx_path.appviewx_path + '/logstash/bin'
            logstash_conf_directory = avx_path.appviewx_path + '/logstash/conf.d/'
            cmd = 'cd ' + logstash_directory + ' ; export JAVA_HOME=' + avx_path.appviewx_path + '/jre/ ; ' + 'nohup ./logstash -f ' + logstash_conf_directory + ' > '+ avx_path.appviewx_path + '/logs/logstash_start.log 2>&1 &'
            command = using_fabric.AppviewxShell([ip], user=username, pty=False)
            lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,cmd))
            l = command.run(cmd)
            lggr.debug('Result of logstash started operation for ip (%s): %s' % (ip,l))
            if list(l[1])[0][1]:
                print_statement('avx_platform_logs', '', ip, port, 'Starting')
            else:
                print(list(l[1])[0][0])
                print_statement('avx_platform_logs', '', ip, port, 'not Started')
            lggr.debug('logstash started for ip : %s has completed' % ip)

     

