"""Script to configure crontab."""
import os
import socket
import sys
from termcolor import colored
import logger
import avx_commons
import signal
from avx_commons import run_local_cmd
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('crontab_configure')
hostname = socket.gethostbyname(socket.gethostname())
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class ConfigureCrontab():
    """Class to configure crontab."""

    def __init__(self, path):
        """__init__ function."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
            self.path = path
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def create_directory(self):
        """."""
        try:
            cron_file = self.path + '/properties/cron_file'
            backup_dir = self.path + '/db_backup'
            if not os.path.isfile(cron_file):
                open(cron_file, 'a').close()
            if not os.path.isdir(backup_dir):
                os.makedirs(backup_dir)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def cron_file_content(self):
        """."""
        try:
            source_mon_cron_file = self.path + '/properties/mon_cron_file'
            source_db_backup_cron = self.path + '/properties/db_backup_cron'
            cron_content = []
            destination = self.path + '/properties/cron_file'
            infile_mon = open(source_mon_cron_file)
            infile_db = open(source_db_backup_cron)
            outfile = open(destination, 'w')
            appviewx_scripts = self.path + '/scripts/'
            appviewx_properties = self.path + '/properties/'
            appviewx_logs = self.path + '/logs/'
            import socket
            hostname = socket.gethostbyname(socket.gethostname())
            start_after_reboot = '@reboot cd ' + appviewx_scripts + ' && ' + self.path + \
                '/Python/bin/python appviewx --start ' + hostname + ' 2>&1'
            replacements = {
                'APPVIEWX_SCRIPTS': appviewx_scripts,
                'APPVIEWX_PROPERTIES': appviewx_properties,
                'APPVIEWX_LOGS': appviewx_logs}
            for line in infile_mon:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                cron_content.append(line + '\n')
            infile_mon.close()
            for line in infile_db:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                cron_content.append(line + '\n')
            logrotate = '0 0 * * * /usr/sbin/logrotate -f ' + self.path + '/db/mongodb/mongodb_log.conf -s ' + self.path + '/logs/mongodb_rotate.log' 
            cron_content.append(logrotate + '\n')
            cron_content.append(start_after_reboot + '\n')
            cron_content = list(filter(
                lambda line: line != '\n', cron_content))
            outfile.writelines(cron_content)
            infile_db.close()
            outfile.close()
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def initialize_cron(self):
        """."""
        try:
            one_time_config_file = current_file_path + '/.one_time_config'
            if not os.path.exists(str(one_time_config_file)):
                run_local_cmd("crontab -r >& /dev/null")
                cron_file = self.path + '/properties/cron_file'
                run_local_cmd('%s %s' % ('crontab', cron_file))
                lggr.debug('Crontab configured')
            else:
                lggr.debug('.one_time_config file already exists')
                print('Crontab not configured!')
                print('Remove the .one_time_config file if you want to configure crontab anyway.')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def env_setup(self):
        """."""
        try:
            with open(os.path.expanduser('~') + '/.bashrc', 'r+') as fd:
                path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(hostname)]
                set_path = 'export PATH=' + path + '/scripts/bin/:$PATH'
                data_readlines = fd.readlines()
                data_readlines = [x.strip('\n') for x in data_readlines]
                if set_path not in data_readlines:
                    fd.write(set_path)
        except Exception as e:
            print (e)
            return False

    def initialize(self):
        """."""
        try:
            self.env_setup()
            self.create_directory()
            self.cron_file_content()
            self.initialize_cron()
            one_time_config_file = current_file_path + '/.one_time_config'
            run_local_cmd('%s %s' % ('touch', one_time_config_file))
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

if __name__ == '__main__':
    try:
        user_input = sys.argv
        if len(user_input) == 1:
            print ('crontab_configure_python takes exactly 1 arguement : path')
            sys.exit(1)
        path = user_input[1]
        obj = ConfigureCrontab(path)
        obj.initialize()
        print(colored('Crontab configuration completed', 'green'))
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
