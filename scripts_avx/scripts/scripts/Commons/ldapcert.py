"""."""
import os
import sys
import logger
import socket
import using_fabric
from avx_commons import return_status_message_fabric
from avx_commons import get_username_path
from config_parser import config_parser

current_dir = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostbyname(socket.gethostname())
lggr = logger.avx_logger('ldap_cert')
attempts = 10
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class LDAPCertificate():
    """."""

    def __init__(self):
        """."""
        conf_file = current_dir + '/../../conf/appviewx.conf'
        self.conf_data = config_parser(conf_file)
        self.path = self.conf_data['ENVIRONMENT']['path'][
            self.conf_data['ENVIRONMENT']['ips'].index(hostname)]

    def generate(self):
        """."""
        pwd = os.getcwd()
        new_path = self.path + '/jre/lib/security'
        os.chdir(new_path)
        gateway_ips = self.conf_data['GATEWAY']['ips']
        gateway_ports = self.conf_data['GATEWAY']['ports']
        for eip, port in zip(gateway_ips, gateway_ports):
            user, path = get_username_path(self.conf_data, eip)
            cmd = 'cd ' + path + '/jre/lib/security && yes 1 | ' + path +\
                '/jre/bin/java -cp ' + path + '/properties/LDAPCertificate' +\
                '.jar InstallCert ' + eip + ':' + port
            command = using_fabric.AppviewxShell([eip], user=user)
            f_obj = command.run(cmd)
            status, res = return_status_message_fabric(f_obj)
            if not status:
                lggr.error('jssecacerts file not formed on: ' + eip)
            else:
                lggr.debug('jssecacerts formed on: ' + eip)
        os.chdir(pwd)
        global attempts
        while attempts:
            if os.path.isfile(self.path + '/jre/lib/security/jssecacerts'):
                break
            else:
                attempts = attempts - 1
                self.generate()

if __name__ == '__main__':
    ob = LDAPCertificate()
    ob.generate()
