"""Mongodb initialization script."""
import sys
import os
import socket
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
import logger
lggr = logger.avx_logger('db_setup python')
import avx_commons
import signal
import getpass
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class DBSetupPython():
    """."""

    def __init__(self):
        """."""
        try:
            from config_parser import config_parser
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    @staticmethod
    def mongo_data_log_files(mongo_data, mongo_logs, conf_data):
        """."""
        try:
            import subprocess
            try:
                folders = os.listdir(mongo_data)
                if len(folders) == 1:
                    cmd = 'mv ' + mongo_data + '/' + folders[0] + ' ' + mongo_data + '/db'
                    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            except:
                pass
            if not os.path.isdir(mongo_data + 'db'):
                db_data_path = mongo_data + 'db/'
                db_log_path = mongo_logs + 'db.log'
                try:
                    os.makedirs(db_data_path)
                    lggr.debug('db folder created at ' + db_data_path)
                except:
                    print('Could not create db_data directory. Exiting!')
                    lggr.error('Could not create db_data directory ' + db_data_path)
                    sys.exit(1)
                if not os.path.exists(db_log_path):
                    try:
                        open(db_log_path, 'w').close()
                    except:
                        print('Could not create db_log file. Exiting!')
                        lggr.error('Could not create db_log file')
                        sys.exit(1)
            else:
                lggr.debug('data directory already exists')
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)

    def set_mongo_conf(self,mongo_logs,log_file_size,log_file_count,mongo_conf_file):
        try:
            conf_content = mongo_logs + '''/db.log{
            \tdaily
            \trotate ''' + log_file_count \
            + '''\n\t\tsize ''' + log_file_size \
            + '''
            \tcreate 700 '''+ getpass.getuser() + ' ' + getpass.getuser() \
+'''\n}'''
            with open(mongo_conf_file,'w') as out_file:
                out_file.write(conf_content)

        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1) 

    def initialize(self):
        """."""
        try:
            path = self.conf_data['ENVIRONMENT']['path'][self.conf_data['ENVIRONMENT']['ips'].index(self.hostname)]
            mongo = path + "/db/mongodb/"
            mongo_data = mongo + "data/"
            mongo_logs = path + "/logs/"
            log_rotate_configure=True
            try:
               log_file_size = self.conf_data['MONGODB']['log_file_size'][0]
               log_file_count = self.conf_data['MONGODB']['log_files_count'][0]
            except Exception:
               lggr.error('LOG_FILE_SIZE or LOG_FILES_COUNT field is missing under MONGODB section')
               log_rotate_configure=False
            mongo_conf_file = mongo + '//mongodb_log.conf'
            self.mongo_data_log_files(mongo_data, mongo_logs, self.conf_data)
            if log_rotate_configure:
               self.set_mongo_conf(mongo_logs,log_file_size,log_file_count,mongo_conf_file)
            return True
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored(e, 'red'))
            sys.exit(1)


if __name__ == '__main__':
    try:
        obj = DBSetupPython()
        obj.initialize()
        print ('db_setup_python completed')
        lggr.info('db folder and db logs created')
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)
