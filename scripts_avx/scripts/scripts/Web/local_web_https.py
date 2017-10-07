"""."""
import os
import sys
import socket
import shutil
import subprocess
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
from avx_commons import run_local_cmd
import logger
lggr = logger.avx_logger('HTTPS_Web')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class LocalWebHTTPS():
    """Class to initialize HTTPS web."""

    def __init__(self):
        """Init function for HTTPS web."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """."""
        try:
            source_myserver_cert = self.conf_data['SSL']['ssl_web_key'][0].replace('{appviewx_dir}', self.path)
            gateway_myserver_cert = self.conf_data['SSL']['ssl_gateway_key'][0].replace('{appviewx_dir}', self.path)

            dest_myserver_cert = self.path + '/jre/bin/myserver.p12'
            shutil.copyfile(source_myserver_cert, dest_myserver_cert)

            web_password = self.conf_data['SSL']['web_key_password'][0]
            cmd = self.path + "/jre/bin/keytool -list -v -keystore " + self.path + \
                "/jre/bin/myserver.p12 -storetype pkcs12 --storepass " + web_password
            process = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            output = process.stdout.decode().strip()
            file_alias = [i for i in output.split('\n') if 'Alias' in i][
                0].split(':')[1].strip()
            myserver_keystore_file_check = self.path + "/jre/bin/myserver.keystore"

            if os.path.exists(myserver_keystore_file_check):
                os.remove(myserver_keystore_file_check)

            pwd = os.getcwd()
            os.chdir(self.path + '/jre/bin')
            keystore_cmd = "yes n | ./keytool " +\
                "-importkeystore -deststorepass keystore -destkeypass " +\
                "keystore -destkeystore myserver.keystore -srckeystore " +\
                "myserver.p12 -srcstoretype PKCS12 " +\
                "-srcstorepass " + web_password + "  -alias '" + file_alias.strip() + "'"
            subprocess.run(keystore_cmd + ' >/dev/null', shell=True)
            lggr.debug('Keystore created')
            os.chdir(pwd)

            myserver_keystore = self.path + '/jre/bin/myserver.keystore'
            dest_myserver_keystore = self.path + '/web/apache-tomcat-web/conf/myserver.keystore'
            if not os.path.exists(myserver_keystore):
                print(myserver_keystore + ' : Missing !!')
                sys.exit(1)
            shutil.copyfile(myserver_keystore, dest_myserver_keystore)
            https_server_template_file = self.path + '/properties/web_https_server.xml'
            https_server_file = self.path + '/web/apache-tomcat-web/conf/server.xml'
            infile = open(https_server_template_file)
            infile_content = infile.readlines()
            infile.close()
            https_port = 'port="' + str(
                self.conf_data['WEB']['ports'][0]) + '" protocol='
            outfile = open(https_server_file, 'w')
            for line in infile_content:
                if '/Installation_Dir/' in line:
                    line = line.replace("/Installation_Dir/", self.path + '/')
                    line = line.replace('port="8443" protocol=', https_port)
                elif 'port="8443" protocol=' in line:
                    line = line.replace('port="8443" protocol=', https_port)
                outfile.write(line)
            outfile.close()

        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)


if __name__ == '__main__':
    try:
        user_input = sys.argv
        if not len(user_input) == 1:
            print('LocalWebHTTPS file takes no arguements!')
            print('exiting!!')
            sys.exit(1)

        ob = LocalWebHTTPS()
        ob.initialize()
        print('HTTPS Web initialized')
        lggr.info('HTTPS Web initialized')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
