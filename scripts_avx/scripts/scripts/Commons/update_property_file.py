"""."""
import os
import socket
import sys
import getpass
from termcolor import colored
import logger
from avx_commons import run_local_cmd
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('update_property')
host_ip = socket.gethostname()
localhost = socket.gethostbyname(socket.gethostname())

class UpdatePropertyFile():
    """."""

    def __init__(self):
        """."""
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
    def list_index_validation(list, index):
        """."""
        try:
            if 0 <= index < len(list):
                return list[index]
            else:
                print ('No Valid Data found')
                return 'ERROR'
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def value_replacement(self):
        """."""
        try:
            try:
                db = []
                for ip, port in zip(self.conf_data['MONGODB']['ips'], self.conf_data['MONGODB']['ports']):
                    db.append(ip + ':' + port)
                db = ','.join(db)
            except:
                pass

            if self.conf_data['ENVIRONMENT']['multinode'][0].upper() == 'FALSE':
                web_host = self.conf_data['WEB']['ips'][0]
                web_port = self.conf_data['WEB']['ports'][0]
                web_sync = web_host + ':5555'
                web_socket = web_host + ':5555'
            else:
                web_host = self.conf_data['WEB']['ips'][0]
                web_port = self.conf_data['WEB']['ports'][0]
                web_sync = ''
                web_socket = ''
                web_nodes = self.conf_data['WEB']['ips']
                try:
                    web_nodes.remove(self.hostname)
                except:
                    pass
                for node in web_nodes:
                    web_sync += node + ':5555,'
                try:
                    web_sync = web_sync.rstrip(',')
                except:
                    pass

                for node in self.conf_data['WEB']['ips']:
                    web_socket += node + ':5555,'
                try:
                    web_socket = web_socket.rstrip(',')
                except:
                    pass
            try:
                if self.conf_data['GATEWAY']['appviewx_gateway_vip'][0] in self.conf_data['GATEWAY']['hosts'] or self.conf_data['GATEWAY']['gateway_vip_enabled'][0].lower() == 'true':
                    ip, port = self.conf_data['GATEWAY']['appviewx_gateway_vip'][0].split(':')
                    appviewx_gateway_base = ip
                    appviewx_gateway_port = port
                else:
                    index = self.conf_data['GATEWAY']['ips'].index(self.hostname)
                    appviewx_gateway_base = self.conf_data['GATEWAY']['ips'][index]
                    appviewx_gateway_port = self.conf_data['GATEWAY']['ports'][index]
            except Exception:
                appviewx_gateway_base = self.conf_data['GATEWAY']['ips'][0]
                appviewx_gateway_port = self.conf_data['GATEWAY']['ports'][0]
            zmq = 'ZMQ_RECEIVER=' + self.hostname + ':5555'

            try:
                web_https = self.conf_data['WEB']['appviewx_web_https'][0]
                if web_https.upper() == 'TRUE':
                    http_tag = 'https'
                else:
                    http_tag = 'http'
            except:
                http_tag = 'http'
            allowed_origins_start = 'ALLOWED_ORGINS=' + http_tag + '://'
            web_eventnotification_url = http_tag + '://' + self.conf_data['WEB']['web_eventnotification_url'][0]

            import json
            with open(self.path + '/properties/hostnames.txt') as hosts_file:
                hosts_content = json.loads(hosts_file.read())

            try:
                try:
                    port_index = self.conf_data['GATEWAY']['ips'].index(localhost)
                except:
                    port_index = 0
                if self.conf_data['SSL']['external_certificate'][0].lower() == 'false':
                    if localhost in self.conf_data['GATEWAY']['ips']:
                        gateway_service_url = localhost + ':' + self.conf_data['GATEWAY']['ports'][port_index] + '/'
                    else:
                        gateway_service_url = self.conf_data['GATEWAY']['ips'][0] + ':' + self.conf_data['GATEWAY']['ports'][0] + '/'

                else:
                    if localhost in self.conf_data['GATEWAY']['ips']:
                        gateway_service_url = self.conf_data['GATEWAY']['ips'][port_index] + ':' + self.conf_data['GATEWAY']['ports'][port_index] + '/'
                    else:
                        gateway_service_url = self.conf_data['GATEWAY']['ips'][0] + ':' + self.conf_data['GATEWAY']['ports'][0] + '/'

                if self.conf_data['GATEWAY'][
                        'appviewx_gateway_https'][0].upper() == 'TRUE':
                    gateway_service_url = 'https://' + gateway_service_url
                else:
                    gateway_service_url = 'http://' + gateway_service_url
            except Exception:
                gateway_service_url = 'http://' + hosts_content[self.conf_data['GATEWAY']['ips'][0]] + ':' + self.conf_data['GATEWAY']['ports'][0]

            if True:
                if self.conf_data['GATEWAY'][
                        'gateway_vip_enabled'][0].upper() == 'TRUE':
                    if self.conf_data['GATEWAY']['appviewx_gateway_vip_https'][0].lower() == 'true':
                        gateway_base_url = 'https://' + appviewx_gateway_base + ':' + appviewx_gateway_port + '/'
                    else:
                        gateway_base_url = 'http://' + appviewx_gateway_base + ':' + appviewx_gateway_port + '/'
                else:
                    gateway_base_url = gateway_service_url

                try:
                    gateway_key = self.conf_data['GATEWAY'][
                        'appviewx_gateway_key'][0]
                    if not len(gateway_key.strip()) > 0:
                        key = open(
                            self.path + '/avxgw/Gateway_key.txt').read().strip()
                        gateway_key = key
                except:
                    gateway_key = ''
                try:
                    gateway_https = self.conf_data['GATEWAY'][
                        'appviewx_gateway_https'][0].upper()
                except:
                    gateway_https = ''

                try:
                    gateway_log_request_size = self.conf_data[
                        'GATEWAY']['gateway_log_request_maxsize'][0]
                except:
                    gateway_log_request_size = ''

                try:
                    gateway_log_debug_size = self.conf_data[
                        'GATEWAY']['gateway_log_debug_maxsize'][0]
                except:
                    gateway_log_debug_size = ''

                try:
                    gateway_log_request_file = self.conf_data[
                        'GATEWAY']['gateway_log_request_maxfiles'][0]
                except:
                    gateway_log_request_file = ''

                try:
                    gateway_log_debug_file = self.conf_data[
                        'GATEWAY']['gateway_log_debug_maxfiles'][0]
                except:
                    gateway_log_debug_file = ''

                try:
                    gateway_log_type = self.conf_data[
                        'GATEWAY']['gateway_log_type'][0]
                except:
                    gateway_log_type = ''

                try:
                    gateway_port = self.conf_data['GATEWAY']['ports'][0]
                except:
                    gateway_port = ''

                try:
                    gateway_source = self.conf_data['GATEWAY'][
                        'appviewx_gateway_source'][0]
                except:
                    gateway_source = 'WEB'
                try:
                    gateway_log_level = self.conf_data['GATEWAY'][
                        'gateway_log_level'][0]
                    if gateway_log_level == '':
                        gateway_log_level = 'INFO'
                except:
                    gateway_log_level = 'INFO'
                try:
                    expiry_notification_limit = self.conf_data['GATEWAY'][
                        'expiry_notification_limit'][0]
                except:
                    expiry_notification_limit = '10'

                gateway_log_path = self.path + '/logs'

            else:
                gateway_source = 'WEB'
                gateway_key = ''
                gateway_service_url = ''
                gateway_port = ''
                gateway_https = ''
                gateway_log_path = ''
                gateway_base_url = ''
                gateway_service_url = ''
                gateway_log_request_size = ''
                gateway_log_debug_size = ''
                gateway_log_request_file = ''
                gateway_log_debug_file = ''
                gateway_log_type = ''
                expiry_notification_limit = '10'

            try:
                web_log_plus_access = self.conf_data[
                    'WEB']['log_plus_access'][0]
            except:
                web_log_plus_access = ''

            try:
                receiver_enabled= self.conf_data['LOGSTASH']['syslog_receiver_enabled'][0]
                syslog_host = self.conf_data['LOGSTASH']['syslog_vip_host'][0]
                syslog_port = self.conf_data['LOGSTASH']['syslog_vip_port'][0]
            except Exception:
                receiver_enabled='False'
                syslog_host = ''
                syslog_port = ''

            try:
                replacement = {
                    '$APPVIEWX_PROPERTIES': self.path + 'properties',
                    '$APPVIEWX_DB_HOST:$APPVIEWX_DB_PORT': db,
                    '${WEB_EVENTNOTIFICATION_URL}': web_eventnotification_url,
                    '$APPVIEWX_WEB_VIP_HOST': web_host,
                    '$APPVIEWX_WEB_VIP_PORT': web_port,
                    'ALLOWED_ORGINS=http://': allowed_origins_start,
                    'ALLOWED_ORGINS=https://': allowed_origins_start,
                    '${GATEWAY_BASE_URL}': gateway_base_url,
                    '${STATISTICS_CONTAINER_VALUE}': '',
                    '${BIGDATA_SOLR_BASE_URL}': '',
                    '${SOURCE_DB_HOSTS}': '',
                    '${DESTINATION_DB_HOST}': '',
                    'ZMQ_RECEIVER=': zmq,
                    'WEB_SYNC=': 'WEB_SYNC=' + web_sync,
                    'WEBSOCKET=': 'WEBSOCKET=' + web_socket,
                    '${WEB_LOG_PLUS_ACCESS}': web_log_plus_access,
                    '${GATEWAY_KEY}': gateway_key,
                    '${GATEWAY_SERVICE_URL}': gateway_service_url,
                    '${GATEWAY_LOG_FILEPATH}': gateway_log_path,
                    '${GATEWAY_PORT}': gateway_port,
                    '${GATEWAY_HTTPS}': gateway_https,
                    '${GATEWAY_LOG_TYPE}': gateway_log_type,
                    '${GATEWAY_LOG_FILEPATH}': gateway_log_path,
                    '${GATEWAY_LOG_DEBUG_MAXFILES}': gateway_log_debug_file,
                    '${GATEWAY_LOG_REQUEST_MAXFILES}': gateway_log_request_file,
                    '${GATEWAY_LOG_DEBUG_MAXSIZE}': gateway_log_debug_size,
                    '${GATEWAY_LOG_LEVEL}': gateway_log_level,
                    '${GATEWAY_LOG_REQUEST_MAXSIZE}': gateway_log_request_size,
                    '${EXPIRY_NOTIFICATION_LIMIT}': expiry_notification_limit,
                    '${SOURCE}': gateway_source,
                    '$APPVIEWX_SYSLOG_RECEIVER_ENABLED':receiver_enabled,
                    '$APPVIEWX_SYSLOG_HOST':syslog_host,
                    '$APPVIEWX_SYSLOG_PORT':syslog_port,
                }
                value_error = [
                    key for key, value in replacement.items()
                    if value == 'ERROR']
                if value_error:
                    value_error = ([s.replace('$', '') for s in value_error])
                    value_error = ([s.replace('{', '') for s in value_error])
                    value_error = ([s.replace('}', '') for s in value_error])
                    print (value_error)
                    sys.exit(1)
            except Exception as e:
                print(colored(e, 'red'))
                sys.exit(1)

            return replacement
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def property_file(self):
        """."""
        try:
            source = self.path + "/properties/template_appviewx_properties"
            destination = self.path + "/properties/appviewx.properties"
            if not os.path.exists(source):
                sys.exit(1)
            replacements = self.value_replacement()
            import re
            if self.conf_data['ENVIRONMENT'][
                    'multinode'][0].upper() == 'FALSE':
                username = getpass.getuser()
                ip_address = self.hostname
            else:
                ip_index = self.conf_data['ENVIRONMENT'][
                    'ips'].index(self.hostname)
                usernames = self.conf_data['ENVIRONMENT']['username']
                if len(usernames) > 1:
                    username = usernames[ip_index]
                else:
                    username = usernames[0]
                ip_address = self.hostname

            try:
                vm_https = self.conf_data['VM_CONF']['vm_https'][0].upper()
            except:
                vm_https = ''

            try:
                key_store_path = self.conf_data['VM_CONF']['key_store_path'][0]
                key_store_path = key_store_path.replace('{appviewx_dir}', self.path)
            except:
                key_store_path = ''

            try:
                key_store_pwd = self.conf_data['VM_CONF']['key_store_pwd'][0]
            except:
                key_store_pwd = ''

            try:
                key_mgr_pwd = self.conf_data['VM_CONF']['key_mgr_pwd'][0]
            except:
                key_mgr_pwd = ''

            try:
                client_cert = self.conf_data[
                    'VM_CONF']['enable_client_cert'][0].upper()
            except:
                client_cert = ''

            try:
                trust_store_path = self.conf_data['VM_CONF']['trust_store_path'][0]
                trust_store_path = trust_store_path.replace('{appviewx_dir}', self.path)
            except:
                trust_store_path = ''

            try:
                trust_store_pwd = self.conf_data[
                    'VM_CONF']['trust_store_pwd'][0]
            except:
                trust_store_pwd = ''

            infile = open(source)
            infile_content = infile.readlines()
            infile.close()
            outfile = open(destination, 'w')

            for line in infile_content:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                if line.strip().startswith('USER_NAME='):
                    line = re.sub(
                        r"USER_NAME=.*", "USER_NAME=" + username, line)
                elif line.strip().startswith('IP_ADDRESS='):
                    line = re.sub(
                        r"IP_ADDRESS=.*",
                        "IP_ADDRESS=" +
                        ip_address,
                        line)
                elif line.strip().startswith('VM_HTTPS='):
                    line = re.sub(r"VM_HTTPS=.*", "VM_HTTPS=" + vm_https, line)
                elif line.strip().startswith('KEY_STORE_PATH='):
                    line = re.sub(
                        r"KEY_STORE_PATH=.*",
                        "KEY_STORE_PATH=" +
                        key_store_path,
                        line)
                elif line.strip().startswith('KEY_STORE_PWD='):
                    line = re.sub(
                        r"KEY_STORE_PWD=.*",
                        "KEY_STORE_PWD=" +
                        key_store_pwd,
                        line)
                elif line.strip().startswith('KEY_MGR_PWD='):
                    line = re.sub(
                        r"KEY_MGR_PWD=.*",
                        "KEY_MGR_PWD=" +
                        key_mgr_pwd,
                        line)
                elif line.strip().startswith('ENABLE_CLIENT_CERT='):
                    line = re.sub(
                        r"ENABLE_CLIENT_CERT=.*",
                        "ENABLE_CLIENT_CERT=" +
                        client_cert,
                        line)
                elif line.strip().startswith('TRUST_STORE_PATH='):
                    line = re.sub(
                        r"TRUST_STORE_PATH=.*",
                        "TRUST_STORE_PATH=" +
                        trust_store_path,
                        line)
                elif line.strip().startswith('TRUST_STORE_PWD='):
                    line = re.sub(
                        r"TRUST_STORE_PWD=.*",
                        "TRUST_STORE_PWD=" +
                        trust_store_pwd,
                        line)
                outfile.write(line)
            outfile.close()
            lggr.debug('appviewx.properties file created')
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

    def update_common_fields(self):
        """."""
        source = self.path + "/properties/appviewx.properties"
        from configobj import ConfigObj
        property_data = ConfigObj(source)
        property_keys = property_data.keys()
        for data in self.conf_data['COMMONS']:
            if data.upper() in property_keys and len(self.conf_data['COMMONS'][data][0]):
                if self.conf_data['COMMONS'][data][0] in ['localhost', '${hostname -i}']:
                    self.conf_data['COMMONS'][data][0] = host_ip
                property_data[data.upper()] = self.conf_data['COMMONS'][data][0]
            if data.strip() == 'version' and 'VERSION_NUMBER' in property_keys and len(self.conf_data['COMMONS'][data][0]):
                property_data['VERSION_NUMBER'] = self.conf_data['COMMONS'][data][0]
        property_data.write()
        run_local_cmd("sed -i 's/ = /=/g' " + source)
        run_local_cmd("sed -i 's/, /,/g' " + source)
        run_local_cmd("sed -i 's@=\"\"@=@g' " +  source)

    def initialize(self):
        """."""
        try:
            self.property_file()
            self.update_common_fields()
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)

if __name__ == '__main__':
    try:
        user_input = sys.argv
        hostname = socket.gethostbyname(socket.gethostname())
        if not len(user_input) == 1:
            print ('update_property_file takes no arguements!')
            sys.exit(1)
        obj = UpdatePropertyFile()
        obj.initialize()
        print (
            colored(
                'appviewx.properties created at ' +
                str(hostname),
                'green'))
    except Exception as e:
        print(colored(e, 'red'))
        lggr.error(e)
        sys.exit(1)
