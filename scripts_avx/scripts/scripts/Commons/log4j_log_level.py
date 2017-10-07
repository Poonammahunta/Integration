"""."""
import os
import socket
import sys
from termcolor import colored
import logger
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('log4j_log_level')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class Log4jLogLevel():
    """Class to initialize Log4jLogLevel."""

    def __init__(self):
        """Init function for Log4jLogLevel."""
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



    def web_log4j(self):
        """."""
        try:
            web_log4j_file = self.path + '/properties/log4j.properties_web'
            self.edit_log4j('WEB', web_log4j_file)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def edit_log4j(self, component, source):
        """."""
        try:
            if not os.path.exists(source):
                print ("%s File not found in %s" %
                       (source.split("/")[-1], source.split("/")[:-1]))
            try:
               if not self.conf_data[
                        component]['log_level'][0]=='':
                  log_4j_template= 'log4j.rootLogger='+self.conf_data[
                        component]['log_level'][0]
               else:
                  log_4j_template= 'log4j.rootLogger=INFO'
            except Exception:
               log_4j_template= 'log4j.rootLogger=INFO'
            with open(source) as infile:
                infile_content = infile.readlines()
            outfile = open(source, 'w')
            for line in infile_content:
                if line.startswith('log4j.rootLogger='):
                    split_value = line.split(',')
                    split_value[0] = log_4j_template
                    line = ','.join(split_value)
                outfile.write(line)
            outfile.close()
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
                self.web_log4j()
            else:
                print('Not a valid component.')
                lggr.error('Not a valid component for log4j')
                sys.exit(1)
            lggr.debug('log4j log level initialized for ' + component)
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
            print('Log4j_level_log file takes exactly 1 arguement.')
            sys.exit()
        component = user_input[1].upper()
        obj = Log4jLogLevel()
        obj.initialize(user_input[1])
        print (
            colored(
                'log4j_log_level initialized for %s' %
                component,
                'green'))
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
