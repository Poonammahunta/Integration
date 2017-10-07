"""."""
import os
import sys
import socket
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import logger
lggr = logger.avx_logger('HTTP_Web')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class LocalWebHTTP():
    """Class to initialize HTTP web."""

    def __init__(self):
        """Init function for HTTP web."""
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
            import shutil
            https_server_template_file = self.path + '/properties/web_http_server.xml'
            https_server_file = self.path + '/web/apache-tomcat-web/conf/server.xml'
            shutil.copyfile(https_server_template_file, https_server_file)
            lggr.debug('server.xml file copied at ' + self.path + '/web/apache-tomcat-web/conf/')
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    try:
        user_input = sys.argv
        if not len(user_input) == 1:
            print('LocalWebHTTP file does not take any arguements.')
            sys.exit(1)
        obj = LocalWebHTTP()
        obj.initialize()
        print('HTTP Web initialized')
        lggr.info('HTTP Web initialized')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
