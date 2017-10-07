#!/usr/bin/python
import os
import sys
import set_path
import using_fabric
import avx_commons
import socket
from termcolor import colored
hostname = socket.gethostbyname(socket.gethostname())
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('WEB')
from ldapcert import LDAPCertificate
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class WebStart():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the web start operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def start(self, web_nodes):
        https_component_values = [self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower(),
                                  self.conf_data['WEB']['appviewx_web_https'][0].lower()]
        """if 'true' in https_component_values:
            LDAPCertificate.generate(LDAPCertificate())"""
        try:
            heap_min = self.conf_data['WEB']['heap_min'][0]
        except Exception:
            heap_min = '1024m'
        try:
            heap_max = self.conf_data['WEB']['heap_max'][0]
        except Exception:
            heap_max = '1280m'
        for ip, port in web_nodes:
            lggr.debug('Starting web in %s' % ip)
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
            lggr.debug('username and path for ip (%s): [%s,%s]' % (ip, username, path))
            log4j_properties = path + "properties/log4j.properties_web "
            cmd = "export PATH=" + \
                path + "/jre/bin:$PATH && export 'JAVA_OPTS=-Xms" + str(heap_min) + " -Xmx" + str(heap_max) + " -XX:PermSize=64M" + \
                " -XX:MaxPermSize=512m -XX:+UseParallelGC -Dappviewx_install_dir=" + path + \
                "  -Dappviewx.property.path=" + path + "/properties/  -Dappviewx_web_port=" + str(port) + \
                " -Dlog4j.configuration=file:" +  \
                log4j_properties + " -Dcom.sun.management.jmxremote=true" + \
                " -Dcom.sun.management.jmxremote.port=4970" + \
                " -Dcom.sun.management.jmxremote.ssl=false" + \
                " -Dappviewx.home=" + path + \
                " -Dcom.sun.management.jmxremote.authenticate=false" + \
                " -Dorg.quartz.scheduler.jmx.export=true -XX:HeapDumpPath=" + path + \
                "/properties/../logs/web_dump -XX:+HeapDumpOnOutOfMemoryError' && nohup " + path + \
                "/web/apache-tomcat-web/bin/startup.sh >/dev/null 2>&1"
            command = using_fabric.AppviewxShell([ip], user=username)
            lggr.debug('Command to starting web for ip (%s) : %s ' % (ip,cmd))
            try:
                res = command.run(cmd)
            except Exception:
                print (colored('Error in communicating with %s' % ip,'red'))
                continue
            lggr.debug('Result of web started operation for ip (%s): %s' % (ip,res))
            if list(res[1])[0][1]:
                print_statement('web', '', ip, port, 'starting')
            else:
                print_statement('web', '', ip, port, 'not started')
            lggr.debug('Web started in ip : %s ' % ip)


if __name__ == '__main__':

    user_input = sys.argv[2:]
    obj = WebStart(user_input)
    obj.start()
