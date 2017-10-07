#../../Python/bin/python
import logbook
import sys
import os
where_am_i = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '../Commons/')
from configobj import ConfigObj
from config_parser import config_parser
import set_path
config = ConfigObj(where_am_i + '/../conf/script.conf')
conf_data = config_parser(where_am_i + '/../../conf/appviewx.conf')
from termcolor import colored
import socket

def info_set(record, handler):
    return record.level_name == 'INFO'


def debug_set(record, handler):
    return record.level_name == 'DEBUG'


def error_set(record, handler):
    return record.level_name == 'ERROR' or record.level_name == 'WARNING'


def syslog_forwarder(conf_data):
    try:
        if conf_data['COMMONS']['syslog_forward'][0].lower() == 'true':
            if not (len(conf_data['COMMONS']['syslog_hosts']) > 1 and len(
                    conf_data['COMMONS']['syslog_hosts'][0])):
                return False
            if not (len(conf_data['COMMONS']['syslog_port']) > 1 and len(
                    conf_data['COMMONS']['syslog_hosts'][0])):
                return False
    except Exception:
        return False


def inject_id(record):
        record.extra['request_id'] = record.filename.split('/')[-1]

def avx_logger(logger_name='avx'):
    root_logger = logbook.Logger(logger_name)
    try:
        zipline_logging = logbook.NestedSetup(
            [logbook.RotatingFileHandler(
                where_am_i + "/../../" +
                config['AVX_SCRIPT_INFO_LOG_FILENAME'],
                filter=info_set,
                max_size=int(config['AVX_SCRIPT_INFO_LOG_MAX_SIZE']),
                backup_count=int(
                    config['AVX_SCRIPT_INFO_LOG_BACKUP_COUNT']),
                mode='a',
                format_string=config['AVX_SCRIPT_INFO_LOG_FORMAT_STRING'],
                bubble=False),
             logbook.RotatingFileHandler(
                 where_am_i + "/../../" +
                 config['AVX_SCRIPT_DEBUG_LOG_FILENAME'],
                 filter=debug_set,
                 max_size=int(config['AVX_SCRIPT_DEBUG_LOG_MAX_SIZE']),
                 mode='a',
                 backup_count=int(
                     config['AVX_SCRIPT_DEBUG_LOG_BACKUP_COUNT']),
                 format_string=config
                 ['AVX_SCRIPT_DEBUG_LOG_FORMAT_STRING'],
                 bubble=False),
             logbook.RotatingFileHandler(
                 where_am_i + "/../../" +
                 config['AVX_SCRIPT_ERROR_LOG_FILENAME'],
                 filter=error_set,
                 max_size=int(config['AVX_SCRIPT_ERROR_LOG_MAX_SIZE']),
                 mode='a',
                 backup_count=int(
                     config['AVX_SCRIPT_ERROR_LOG_BACKUP_COUNT']),
                 format_string=config
                 ['AVX_SCRIPT_ERROR_LOG_FORMAT_STRING'],
                 bubble=False), 
             logbook.Processor(inject_id), ])
    except Exception:
        hostname = socket.gethostbyname(socket.gethostname())
        index = conf_data['ENVIRONMENT']['ips'].index(hostname)
        path = conf_data['ENVIRONMENT']['path'][index]
        log_path = os.path.abspath(path + '/logs')
        if not os.path.isdir(log_path):
            print(colored('logs directory not found at ' + log_path, 'red'))
        else:
            print (colored("Error in script.conf file", "red"))
        sys.exit(1)
    if conf_data['COMMONS']['syslog_forward'][0].lower() == 'true':
        if not(len(conf_data['COMMONS']['syslog_hosts']) > 1
               and len(conf_data['COMMONS']['syslog_hosts'][0])):
            print (
                colored(
                    "Error in SYSLOG_HOSTS field in conf file..It should not be empty value in conf file",
                    "red"))
            sys.exit(1)
        if not(len(conf_data['COMMONS']['syslog_port']) > 1
               and len(conf_data['COMMONS']['syslog_port'][0])):
            print (
                colored(
                    "Error in SYSLOG_PORTS field in conf file..It should not be empty value in conf file",
                    "red"))
            sys.exit(1)
        syslog = logbook.SysLogHandler(
            address=(
                conf_data['COMMONS']
                ['syslog_hosts'][0],
                conf_data['COMMONS']
                ['syslog_port'][0]))
    zipline_logging.push_application()
    return root_logger
