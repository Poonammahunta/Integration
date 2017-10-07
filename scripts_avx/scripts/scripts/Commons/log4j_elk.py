"""."""
import os
import socket
import sys
from termcolor import colored
import logger
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('log4j_elk')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class Log4jelk():
    """Class to initialize Log4jelk."""

    def __init__(self):
        """Init function for Log4jelk."""
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

    @staticmethod
    def find_and_replace(filename, partial, replacement):
        """."""
        try:
            with open(filename) as open_file:
                file_content = open_file.readlines()
            for line in file_content:
                if partial in line:
                    file_content[
                        file_content.index(line)] = '\t' + '  ' + replacement + '\n'
                    break
            with open(filename, 'w')as open_file:
                for line in file_content:
                    open_file.write(line)
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)



    def web_log4jelk(self):
        """."""
        try:
            log4j_web = self.path + '/properties/elk/log4j_web.xml'

            replacement = "<param name=\"Port\" value=\"%s\"/>" % self.conf_data[
                'WEB']['log_plus_web_port'][0]
            response = self.find_and_replace(log4j_web, "Port", replacement)

            replacement = "<param name=\"RemoteHost\" value=\"%s\"/>" % self.conf_data[
                'WEB']['log_plus_web_vip'][0]
            response = self.find_and_replace(
                log4j_web, "RemoteHost", replacement)

            replacement = "<param name=\"level\" value=\"%s\"/>" % self.conf_data[
                'WEB']['log_level'][0]
            response = self.find_and_replace(log4j_web, "level", replacement)
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self, component):
        """."""
        try:
            if component == 'WEB':
                self.web_log4jelk()
            else:
                print ('Not a valid component')
                lggr.error('Not a valid component for log4j elk')
                sys.exit(1)
            lggr.debug('Log4j_elk initialized for ' + component)
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    try:
        user_input = sys.argv
        if not len(user_input) == 2:
            print ('Log4j_elk file takes exactly 1 arguement')
            sys.exit(1)
        component = user_input[1].upper()
        obj = Log4jelk()
        obj.initialize(component)
        print(colored('log4j_elk initialized for %s' % component, 'green'))
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
