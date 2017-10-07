#!../../Python/bin/python
"""File to perform plugin log4j initialization across the nodes."""
import os
import sys
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import logger
import socket
lggr = logger.avx_logger('vm_log4j')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class PluginLog4j():
    """The class to initialize common components."""

    def __init__(self):
        """."""
        self.path = os.path.dirname(os.path.dirname(current_file_path))
        self.plugin_log4j_files = []
        self.hostname = socket.gethostbyname(socket.gethostname())

    def edit_content(self):
        """."""
        try:
            for file in self.plugin_log4j_files:
                str_to_replace = "{appviewx_dir}"
                infile = open(file)
                content = infile.readlines()
                content = list(filter(lambda line: line != '\n', content))
                infile.close()
                outfile = open(file, 'w+')
                for line in content:
                    if str_to_replace in line:
                        line = line.replace(str_to_replace, self.path)
                    outfile.write(line)
                outfile.close()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def get_log_files(self, path):
        """."""
        try:
            os.chdir(path)
            for file in os.listdir(path):
                dirname, filename = os.path.split(os.path.abspath(file))
                file = dirname + '/' + filename
                if os.path.isdir(file):
                    self.get_log_files(file)
                    os.chdir('..')
                else:
                    if file.split('/')[-1].startswith('log4j.'):
                        lggr.debug('Log file found: ' + file.split('/')[-1])
                        self.plugin_log4j_files.append(file)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def initialize(self,):
        """."""
        try:
            if os.path.isdir(self.path + '/Plugins'):
                self.get_log_files(self.path + '/Plugins/')
                self.plugin_log4j_files.append(
                    self.path + '/properties/log4j.avx-crontab')
                print(self.plugin_log4j_files)
                self.edit_content()
            else:
                print(self.path + '/Plugins directory not found on: ' +
                      self.hostname)
                lggr.error('Plugins directory not found!')
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

if __name__ == '__main__':
    ob = PluginLog4j()
    ob.initialize()
    lggr.info('VM Logs initialized')
