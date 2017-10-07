#!/usr/bin/python
import os
import sys
from avx_commons import get_username_path,help_fun
import using_fabric
import set_path
from termcolor import colored
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('WEB')
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class WebStop():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the web stop operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def stop(self, web_nodes):
        for ip, port in web_nodes:
            lggr.debug('Stopping web in %s' % ip)
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
            lggr.debug('username and path for ip (%s): [%s,%s]' % (ip, username, path))
            cmd = path + 'Python/bin/python ' + path + '/scripts/Web/web_stop.py ' + port
            command = using_fabric.AppviewxShell([ip], user=username)
            lggr.debug('Calling script stopping web for ip (%s): %s ' % (ip,cmd))
            try:
                l = command.run(cmd)
            except Exception:
                print (colored('Error in communicating with %s' % ip,'red'))
                continue
            lggr.debug('Result of stopping web in ip (%s): %s' % (ip,l))
            if list(l[1])[0][1]:
                print_statement('web', '', ip, port, colored('stopped', 'red'))
            else:
                print(list(l[1])[0][0])
                print_statement('web', '', ip, port, colored('not stopped', 'red'))
            lggr.debug('Stopping web in %s has completed' % ip)

