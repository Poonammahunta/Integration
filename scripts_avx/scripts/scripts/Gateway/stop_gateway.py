#!/usr/bin/python
import os
import sys
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
from avx_commons import get_username_path
import using_fabric
import set_path
from termcolor import colored
import logger
lggr = logger.avx_logger('GATEWAY')
avx_path = set_path.AVXComponentPathSetting()
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
class GatewayStop():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the gateway stop operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def stop(self,gateway_nodes):
        for ip, port in gateway_nodes:
            lggr.debug('Stopping gateway in %s' % ip)
            lggr.info('Stopping gateway in %s' % ip)
            try:
                username, path = get_username_path(
                    self.conf_data, ip)
                lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
            command = using_fabric.AppviewxShell([ip], user=username)
            cmd = path + '/Python/bin/python ' + path + '/scripts/Gateway/gateway_stop.py ' + port
            lggr.debug('Calling script to stop gateway : %s' % cmd)
            try:
              l = command.run(cmd)
            except Exception:
              print (colored('Error in communicating with %s' % ip,'red'))
              continue
            lggr.debug('Result of service started operation for ip (%s): %s' % (ip,l))
            if list(l[1])[0][1]:
                print_statement('gateway', '', ip, port, 'stopped')
            else:
                print('gateway', '', ip, port, 'not stopped')
            lggr.debug('Gateway stopped in ip : %s' % ip)
