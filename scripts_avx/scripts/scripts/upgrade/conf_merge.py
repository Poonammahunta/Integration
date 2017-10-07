#!/../../Python/bin/python
import os
import sys
import traceback
import configparser
import getpass
import socket
currentframe = os.path.dirname(os.path.realpath(__file__))
if not os.path.realpath('Commons/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Commons/'))
if not os.path.realpath('Mongodb/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Mongodb/'))
if not os.path.realpath('Web/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Web/'))
if not os.path.realpath('Gateway/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Gateway/'))
if not os.path.realpath('Plugins/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Plugins/'))
import logging
import avx_commons
import logger
lggr = logger.avx_logger('AppViewX')
import avx_commons
import signal
from configobj import ConfigObj
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
hostname = socket.gethostbyname(socket.gethostname())
lggr.debug('hostname:'+str(hostname))
currentframe = os.path.dirname(os.path.realpath(__file__))
lggr.debug('Script Path:'+str(currentframe))
python_location = currentframe + '/../Python/bin/python '
lggr.debug('Python Path:'+str(python_location))
appviewx_location = currentframe
appviewx_location= appviewx_location.split('scripts')[0]
base_conf_file= currentframe + '/../../conf/appviewx_backup.conf'
new_conf_file = currentframe + '/../../conf/appviewx.conf'
hostname = socket.gethostbyname(socket.gethostname())
def get_base_version():
        with open(base_conf_file,'r') as in_file:
            base_conf_content = in_file.readlines()
        for line in base_conf_content:
            if "VERSION" in line:
                base_version = line.strip("VERSION_NUMBER=")
                base_version = base_version.strip("V")
                base_version = base_version.strip('v')
                break
        lggr.debug('base version is identified as ' + base_version)
        return base_version
def merge_conf_data(base_version):

        if not base_version >= "12.0.0":
            lggr.debug('Base version is higher than 12.0.0')
            with open(base_conf_file,'r') as in_file:
                content = in_file.readlines()
            config = configparser.SafeConfigParser()
            config.optionxform =str
            config.read(new_conf_file)
            temp_conf = ConfigObj(os.path.abspath(currentframe + '/../../conf/plugins.meta'))
            plug_data = temp_conf['PLUGINS']
            try:
                logstash_data = temp_conf['LOGSTASH']
                logstash_hosts = logstash_data['HOSTS']
                if 'str' in str(type(logstash_hosts)):
                    logstash_hosts = logstash_data['HOSTS']
                elif 'list' in str(type(logstash_hosts)):
                    logstash_hosts = ','.join(logstash_data['HOSTS'])
                logstash_log_level = logstash_data['LOG_LEVEL']
            except:
                logstash_data = {}
                lggr.error('LOGSTASH values not present in plugins.')

            try:
                ext_cert = temp_conf['SSL']['External_Certificate']
            except:
                ext_cert = 'False'
            try:
                ssh_port = temp_conf['ENVIRONMENT']['SSH_PORT']
            except:
                ssh_port = '22'

            config.remove_section('PLUGINS')
            config.add_section('PLUGINS')

            section = 'ENVIRONMENT'

            lggr.debug('obtained conf data from advanced version')
            for line in content:
                line = line.strip()
                if line.startswith('['):
                    section = line.lstrip('[').rstrip(']')
                if not (line.startswith('#') or line.startswith('\n')) and not (line.strip('\n').isspace() or line.strip('\n') == ''):
                        field_value = line.split('=')[1].strip()
                        key_value = line.split('=')[0].strip()
                        if key_value == 'APPVIEWX_SSH':
                            config.set('ENVIRONMENT','MULTINODE',field_value)
                        elif key_value == 'APPVIEWX_SSH_USERNAME':
                            config.set('ENVIRONMENT','SSH_HOSTS',field_value)
                        elif key_value == 'APPVIEWX_SSH_HOSTS':
                            if config.get('ENVIRONMENT','MULTINODE').upper() == 'TRUE':
                                ssh_hosts = field_value.split(',')
                                username = config.get('ENVIRONMENT','SSH_HOSTS')
                                if ',' in username:
                                    usernames = username.split(',')
                                else:
                                    usernames = list()
                                    usernames.append(username)  
                                for i in range(len(ssh_hosts)):
                                    if len(usernames) > 1:
                                        if i == 0:
                                            field = usernames[i] + '@' + ssh_hosts[i]
                                        else:
                                            field = field + ',' + usernames[i] + '@' + ssh_hosts[i]
                                    else:
                                        if i == 0:
                                            field = usernames[0] + '@' + ssh_hosts[i]
                                        else:
                                            field = field + ',' + usernames[0] + '@' + ssh_hosts[i]
                                config.set('ENVIRONMENT','SSH_HOSTS',field)
                            else:
                                hosts = getpass.getuser() + '@localhost' + ':' + appviewx_location
                                config.set('ENVIRONMENT','SSH_HOSTS',hosts)
                        elif key_value == 'DATACENTER':
                            if config.get('ENVIRONMENT', 'MULTINODE').upper() == 'TRUE':
                                field_value = field_value.replace(" ", " && ")
                                config.set('ENVIRONMENT','DATACENTER',field_value)
                            else:
                                field_value = "Absecon:localhost"
                                config.set('ENVIRONMENT','DATACENTER',field_value)
                        elif key_value == 'DEFAULT_DATACENTER':
                            config.set('ENVIRONMENT','DEFAULT_DATACENTER',field_value)
                        elif key_value == 'APPVIEWX_DB_HOST':
                            mongo_multinode = config.get('ENVIRONMENT','MULTINODE')
                            if not mongo_multinode.upper() == 'TRUE':
                                config.set('MONGODB','HOSTS','localhost')
                        elif key_value == 'APPVIEWX_DB_PORT':
                            mongo_multinode = config.get('ENVIRONMENT','MULTINODE')
                            if not mongo_multinode.upper() == 'TRUE':
                                mongo_host = config.get('MONGODB','HOSTS')
                                mongo_host = mongo_host + ':' +field_value
                                config.set('MONGODB','HOSTS',mongo_host)
                        elif key_value == 'APPVIEWX_DB_PRIMARY_HOST':
                            mongo_multinode = config.get('ENVIRONMENT','MULTINODE')
                            if mongo_multinode.upper() == 'TRUE':
                                config.set('MONGODB','HOSTS',field_value)
                        elif key_value == 'APPVIEWX_DB_PRIMARY_PORT':
                            mongo_multinode = config.get('ENVIRONMENT','MULTINODE')
                            if mongo_multinode.upper() == 'TRUE':
                                mongo_host = config.get('MONGODB','HOSTS')
                                mongo_host = mongo_host + ':' + field_value
                                config.set('MONGODB','HOSTS',mongo_host)
                        elif key_value == 'APPVIEWX_DB_SECONDARY_HOSTS':
                            mongo_multinode = config.get('ENVIRONMENT','MULTINODE')
                            if mongo_multinode.upper() == 'TRUE':
                                mongo_host = config.get('MONGODB','HOSTS')
                                mongo_host = mongo_host + ',' + field_value
                                config.set('MONGODB','HOSTS',mongo_host)
                        elif key_value == 'APPVIEWX_GATEWAY_HOST':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if not multinode.upper() == 'TRUE':
                                # config.set('GATEWAY','MULTINODE','FALSE')
                                config.set('GATEWAY','HOSTS','localhost')
                        elif key_value == 'APPVIEWX_GATEWAY_PORT':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if not multinode.upper() == 'TRUE':
                                # config.set('GATEWAY','MULTINODE','FALSE')
                                gateway_host = config.get('GATEWAY','HOSTS')
                                gateway_host = gateway_host + ':' + field_value
                                config.set('GATEWAY','HOSTS',gateway_host)
                        elif key_value == 'APPVIEWX_GATEWAY_HOSTS':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if multinode.upper() == 'TRUE':
                                # config.set('GATEWAY','MULTINODE','TRUE')
                                config.set('GATEWAY','HOSTS',field_value)
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                        elif key_value == 'APPVIEWX_WEB_MULTI_NODE':
                            # config.set('WEB','MULTINODE',field_value)
                            pass
                        elif key_value == 'APPVIEWX_WEB_HOST':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if multinode.upper() == 'FALSE':
                                config.set('WEB','HOSTS','localhost')
                        elif key_value == 'APPVIEWX_WEB_PORT':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if multinode.upper() == 'FALSE':
                                web_host = config.get('WEB','HOSTS')
                                web_host = web_host + ':' + field_value
                                config.set('WEB','HOSTS',web_host)
                        elif key_value == 'APPVIEWX_WEB_HOSTS':
                            multinode = config.get('ENVIRONMENT','MULTINODE')
                            if multinode.upper() == 'TRUE':
                                config.set('WEB','HOSTS',field_value)
                        elif key_value == 'APPVIEWX_WEB_HTTPS':
                            config.set('WEB','APPVIEWX_WEB_HTTPS',field_value)
                        elif key_value == 'APPVIEWX_SSL_WEB_KEY':
                            config.set('SSL','ssl_web_key',field_value)
                        elif key_value == 'APPVIEWX_SSL_GATEWAY_KEY':
                            config.set('SSL','ssl_gateway_key',field_value)
                        elif key_value == 'APPVIEWX_GATEWAY_HTTPS':
                            config.set('GATEWAY','APPVIEWX_GATEWAY_HTTPS',field_value)
                        elif key_value == 'EXPORT_GATEWAY_PASSWORD':
                            config.set('SSL','gateway_key_password',field_value)
                        elif key_value == 'EXPORT_WEB_PASSWORD':
                            config.set('SSL','web_key_password',field_value)
                        elif key_value == 'TIME_ZONE_FORMAT':
                            config.set('COMMONS','TIME_ZONE',field_value)
                        elif key_value == 'GATEWAY_LOG_REQUEST_MAXSIZE':
                            config.set('GATEWAY','GATEWAY_LOG_REQUEST_MAXSIZE',field_value)
                        elif key_value == 'GATEWAY_LOG_DEBUG_MAXFILES':
                            config.set('GATEWAY','GATEWAY_LOG_DEBUG_MAXFILES',field_value)
                        elif key_value == 'GATEWAY_LOG_REQUEST_MAXFILES':
                            config.set('GATEWAY','GATEWAY_LOG_REQUEST_MAXFILES',field_value)
                        elif key_value == 'GATEWAY_LOG_DEBUG_MAXSIZE':
                            config.set('GATEWAY','GATEWAY_LOG_DEBUG_MAXSIZE',field_value)
                        elif key_value == 'EXPIRY_NOTIFICATION_LIMIT':
                            config.set('GATEWAY','EXPIRY_NOTIFICATION_LIMIT',field_value)
                        elif key_value == 'APPVIEWX_EMAIL_ADDRESS':
                            config.set('COMMONS','EMAIL_FROM_ADDRESS',field_value)
                        elif key_value == 'APPVIEWX_SMTP_SERVER':
                            config.set('COMMONS','EMAIL_HOST',field_value)
                        elif key_value == 'APPVIEWX_SMTP_PORT':
                            config.set('COMMONS','EMAIL_PORT',field_value)
                        elif key_value == 'APPVIEWX_SNMP_SOURCE_ADDRESS':
                            config.set('COMMONS','SNMP_SOURCE_ADDRESS',field_value)
                        elif key_value == 'APPVIEWX_SNMP_COMMUNITY':
                            config.set('COMMONS','SNMP_COMMUNITY',field_value)
                        elif key_value == 'APPVIEWX_SNMP_APPVIEWX_OID':
                            config.set('COMMONS','SNMP_APPVIEWX_OID',field_value)
                        elif key_value == 'APPVIEWX_SYSLOG_RECEIVER_ENABLED':
                            config.set('COMMONS','SYSLOG_RECEIVER_ENABLED',field_value)
                        elif key_value == 'APPVIEWX_SYSLOG_HOST':
                            config.set('COMMONS','SYSLOG_HOST',field_value)
                        elif key_value == 'APPVIEWX_SYSLOG_PORT':
                            config.set('COMMONS','SYSLOG_PORT',field_value)
                        elif key_value == 'APPVIEWX_TRAP_RECEIVER_ENABLED':
                            config.set('COMMONS','TRAP_RECEIVER_ENABLED',field_value)
                        elif key_value == 'APPVIEWX_TRAP_RECEIVER_HOST':
                            config.set('COMMONS','TRAP_RECEIVER_HOST',field_value)
                        elif key_value == 'APPVIEWX_TRAP_RECEIVER_PORT':
                            config.set('COMMONS','TRAP_RECEIVER_PORT',field_value)
                        elif key_value == 'APPVIEWX_TRAP_RECEIVER_COMMUNITY':
                            config.set('COMMONS','TRAP_RECEIVER_COMMUNITY',field_value)
                        elif key_value == 'IHEALTH_PROXY':
                            config.set('COMMONS','IHEALTH_PROXY',field_value)
                        elif key_value == 'PROXY_AUTH_MODE':
                            config.set('COMMONS','PROXY_AUTH_MODE',field_value)
                        elif key_value == 'PROXY_HOST':
                            config.set('COMMONS','PROXY_HOST',field_value)
                        elif key_value == 'PROXY_USERNAME':
                            config.set('COMMONS','PROXY_USERNAME',field_value)
                        elif key_value == 'PROXY_PASSWORD':
                            config.set('COMMONS','PROXY_PASSWORD',field_value)
                        elif key_value == 'APPVIEWX_AKAMAI_PROXY':
                            config.set('COMMONS','AKAMAI_PROXY_HOST',field_value)
                        elif key_value == 'EVENT_NOTIFICATION_URL':
                            config.set('COMMONS','EVENT_NOTIFICATION_URL',field_value)
                        elif key_value == 'LOGIN_ORDER':
                            config.set('COMMONS','LOGIN_ORDER',field_value)
                        elif key_value == 'REDIRECT_APPVIEWX_LOG_INTO_LOG4J':
                            config.set('COMMONS','REDIRECT_APPVIEWX_LOG_INTO_LOG4J',field_value)
                        elif key_value == 'SCRIPT_EXECUTION_ENABLED':
                            config.set('COMMONS','SCRIPT_EXECUTION_ENABLED',field_value)
                        elif key_value == 'DEVICE_SSH_PORT':
                            config.set('COMMONS','DEVICE_SSH_PORT',field_value)
                        elif key_value == 'DISABLE_INACTIVE_USER':
                            config.set('COMMONS','DISABLE_INACTIVE_USER',field_value)
                        elif key_value == 'MAX_IN_ACTIVE_DAYS_ALLOWED':
                            config.set('COMMONS','MAX_IN_ACTIVE_DAYS_ALLOWED',field_value)
                        elif key_value == 'LOGIN_TRIAL_ENABLED':
                            config.set('COMMONS','LOGIN_TRIAL_ENABLED',field_value)
                        elif key_value == 'LOGIN_TRIAL_COUNT':
                            config.set('COMMONS','LOGIN_TRIAL_COUNT',field_value)
                        elif key_value == 'REVERSE_LOOKUP_TRIGGER':
                            config.set('COMMONS','REVERSE_LOOKUP_TRIGGER',field_value)
                        elif key_value == 'GATEWAY_LOG_TYPE':
                            config.set('GATEWAY','GATEWAY_LOG_TYPE',field_value)
                        elif key_value == 'KEY_DISCOVER_REQUIRED':
                            config.set('COMMONS','KEY_DISCOVER_REQUIRED',field_value)
                        elif key_value == 'GATEWAY_BASE_URL':
                            config.set('COMMONS','GATEWAY_BASE_URL',field_value)
                        elif key_value == 'APPVIEWX_CPU_MEM_MONITOR_POLL_INTERVAL' or key_value == 'APPVIEWX_CPU_MONITOR_POLL_INTERVAL':
                            config.set('COMMONS','APPVIEWX_CPU_MONITOR_POLL_INTERVAL',field_value)
                        elif key_value == 'APPVIEWX_MEMORY_USAGE_CRITICAL':
                            config.set('COMMONS','APPVIEWX_MEMORY_USAGE_CRITICAL',field_value)
                        elif key_value == 'APPVIEWX_MEMORY_USAGE_NOTIFY':
                            config.set('COMMONS','APPVIEWX_MEMORY_USAGE_NOTIFY',field_value)
                        elif key_value == 'APPVIEWX_CPU_USAGE_CRITICAL':
                            config.set('COMMONS','APPVIEWX_CPU_USAGE_CRITICAL',field_value)
                        elif key_value == 'FTP_USERNAME':
                            config.set('COMMONS','FTP_USERNAME',field_value)
                        elif key_value == 'FTP_PASSWORD':
                            config.set('COMMONS','FTP_PASSWORD',field_value)
                        elif key_value == 'FTP_SERVER':
                            config.set('COMMONS','FTP_SERVER',field_value)
                        elif key_value == 'FTP_PORT':
                            config.set('COMMONS','FTP_PORT',field_value)
                        elif key_value == 'FTP_REMOTE_DIR':
                            config.set('COMMONS','FTP_REMOTE_DIR',field_value)
                        elif key_value == 'ELASTIC_HOST':
                            config.set('COMMONS','ELASTIC_HOST',field_value)
                        elif key_value == 'LOG_PLUS_ACCESS':
                            config.set('WEB','LOG_PLUS_ACCESS',field_value)
                        elif key_value == 'LOG_PLUS_WEB_VIP':
                            config.set('WEB','LOG_PLUS_WEB_VIP',field_value)
                        elif key_value == 'LOG_PLUS_WEB_PORT':
                            config.set('WEB','LOG_PLUS_WEB_PORT',field_value)
                        elif key_value == 'PERCENTAGE_CPU':
                            config.set('COMMONS','PERCENTAGE_CPU',field_value)
                        elif key_value == 'PERCENTAGE_THROUGHPUT':
                            config.set('COMMONS','PERCENTAGE_THROUGHPUT',field_value)
                        elif key_value == 'PERCENTAGE_MEMORY':
                            config.set('COMMONS','PERCENTAGE_MEMORY',field_value)
                        elif key_value == 'MAX_THROUGHPUT_RATE_PER_SECOND':
                            config.set('COMMONS','MAX_THROUGHPUT_RATE_PER_SECOND',field_value)
                        elif key_value == 'WEB_EVENTNOTIFICATION_URL':
                            config.set('COMMONS','WEB_EVENTNOTIFICATION_URL',field_value)
                        elif key_value == 'IP_ADDRESS':
                            config.set('COMMONS','IP_ADDRESS',field_value)
                        elif key_value == 'SYSLOG_FORWARD':
                            config.set('COMMONS','SYSLOG_FORWARD',field_value)
                        elif key_value == 'APPVIEWX_CPU_USAGE_NOTIFY ':
                            config.set('COMMONS','APPVIEWX_CPU_USAGE_NOTIFY',field_value)
                        elif key_value == 'APPVIEWX_GATEWAY_VIP':
                            config.set('GATEWAY','APPVIEWX_GATEWAY_VIP',field_value)
                        elif key_value == 'LOG_PLUS_HOST':
                            config.set('COMMONS','LOG_PLUS_HOST',field_value)
                        elif key_value == 'CSR_PASSWORD':
                            config.set('SSL','web_key_password',field_value)
                            config.set('SSL','gateway_key_password',field_value)
                        elif key_value == 'APPVIEWX_DB_ARBITER_HOST':
                            arbiter_host = None
                            arbiter_host = field_value 
                        elif key_value == 'APPVIEWX_DB_ARBITER_PORT':
                            if arbiter_host:
                                arbiter_host = arbiter_host + ':' + field_value
                            config.set('MONGODB','ARBITER_HOSTS',arbiter_host)
                        config.set('WEB','APPVIEWX_WEB_HTTPS','TRUE')
                        config.set('GATEWAY','APPVIEWX_GATEWAY_HTTPS','TRUE')
                elif line.startswith('#'):
                    config.set(section, line, '')
            config.set('SSL', 'External_Certificate', ext_cert)
            config.set('ENVIRONMENT', 'SSH_PORT', ssh_port)

            all_plugins = []
            for key, value in plug_data.items():
                if 'list' in str(type(value)):
                    value = ','.join(value)
                all_plugins.append(key.lower())
                config.set('PLUGINS', key, value)
            config.set('PLUGINS', 'ENABLED_PLUGINS', ','.join(all_plugins))

            for key, value in logstash_data.items():
                if 'list' in str(type(value)):
                    value = ','.join(value)
                config.set('LOGSTASH', key, value)

            # Merging Comments with Original Configuration file
            f = open(new_conf_file).readlines()
            lis = []
            location = None
            for line in f:
                try:
                    key, b = map(str.strip, line.split("="))
                    lis.append(" = ".join([key, str(config.get(location, key))]) + "\n")
                except:
                    if line.startswith("["):
                        location = line[1:len(line)-2]
                        lis.append("\n"+line)
                    elif line.startswith("#"):
                        lis.append(line)
            g = open(new_conf_file, 'w')
            lis = list(filter(lambda line: line != '\n', lis))
            g.writelines(lis)
            """
            with open(new_conf_file,'w') as out_file:
                config.write(out_file)
            """

if __name__ == "__main__":
    template_file = currentframe + '/../../conf/plugins.meta'
    if not os.path.isfile(template_file):
        print('plugins.meta not found!')
        sys.exit(1)
    base_version = get_base_version()
    merge_conf_data(base_version)
