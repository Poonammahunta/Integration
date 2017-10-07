"""Initialize Java Security."""
import os
import socket
import sys
from termcolor import colored
import logger
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('java_security_init')

import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
class JavaSecurity():
    """Class to Initialize Java Security."""

    def __init__(self):
        """The init function."""
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
    def change_data(source, destination):
        """Funtion to edit contents of file."""
        try:
            infile_content = list()
            infile = open(source)
            infile_content = infile.readlines()
            infile.close()
            outfile = open(destination, 'w')
            str_to_check = 'jdk.certpath'
            str_to_replace = '#jdk.certpath'
            for line in infile_content:
                if '#jdk.certpath' in line:
                    outfile.write(line)
                    continue
                if str_to_check in line:
                    line = line.replace(str_to_check, str_to_replace)
                outfile.write(line)
            outfile.close()
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def initialize(self):
        """Function to start java security."""
        try:
            java_home = self.path + '/jre/'
            source = java_home + 'lib/security/java.security'
            destination = java_home + 'lib/security/java.security'
            try:
                self.change_data(source, destination)
            except Exception as e:
                print(e)
                sys.exit(1)
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    """Start the execution of script."""
    try:
        lggr.info('inside java_security_python')
        user_input = sys.argv
        if not len(user_input) == 1:
            print('java_security file takes no input')
            sys.exit(1)
        lggr.debug('Starting Java Security initialization')
        obj = JavaSecurity()
        obj.initialize()
        print(colored('Java Security configuration completed.', 'green'))
        lggr.debug('Java Security configuration completed.')
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
