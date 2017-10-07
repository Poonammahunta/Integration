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
lggr = logger.avx_logger('GATEWAY')
import avx_commons
from avx_commons import print_statement
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class GatewayStart():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the gateway start operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def start(self, gateway_nodes):
        for ip, port in gateway_nodes:
            lggr.debug('Starting gateway in %s' % ip)
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
            dc_cmd = 'export datacenter=' + datacenter
            process_name = path + 'avxgw/avxgw '
            node_properties = path + 'properties/appviewx.properties '
            cmd = 'cd ' + path + '/avxgw/ ; ' + process_name + ' ' + node_properties + ' >> /dev/null 2>&1 &'
            lggr.debug('command for starting gateway: %s' % cmd)
            command = using_fabric.AppviewxShell(
                [ip], user=username, pty=False)
            lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,dc_cmd))
            try:
              l = command.run(dc_cmd)
            except Exception:
              print (colored('Error in communicating with %s' % ip,'red'))
              continue
            if (list(l[1])[0][1]) == False:
                print_statement('gateway', '', ip, port, 'not started')
                continue
            lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,cmd))
            l = command.run(cmd)
            lggr.debug('Result of gateway started operation for ip (%s): %s' % (ip,l))
            if list(l[1])[0][1]:
                print_statement('gateway', '', ip, port, 'starting')
            else:
                print(list(l[1])[0][0])
                print_statement('gateway', '', ip, port, 'not started')
            lggr.debug('Gateway started for ip : %s has completed' % ip)

