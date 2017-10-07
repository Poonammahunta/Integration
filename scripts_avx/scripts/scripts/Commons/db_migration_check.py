"""."""
from pymongo import MongoClient
from configobj import ConfigObj
import os
import subprocess
import socket
import warnings
import json
import sys
import logger
lggr = logger.avx_logger('db_migration_status')
import time
warnings.filterwarnings("ignore")

current_location = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostbyname(socket.gethostname())


class DBMIGRATIONCHECK():
    """Main class for verifying the db migration ."""

    def __init__(self, time, conf_file_path):
        """."""
        if not os.path.exists(conf_file_path):
            sys.exit("Kindly enter a valid Conf File Path")
        self.time = time
        self.conf_data = ConfigObj(conf_file_path)

    def get_mongo_object(self):
        """."""
        try:
            version = self.conf_data['VERSION_NUMBER']
        except KeyError:
            version = self.conf_data['COMMONS']['VERSION']
        except Exception:
            sys.exit("Unable to get the version of AppViewX")
        try:
            version = version.strip('v')
            property_file = current_location + \
                '/../../properties/appviewx.properties'
            property_data = ConfigObj(property_file)

            mongo_username = property_data['MONGO_USERNAME']
            mongo_encryp_pass = property_data['MONGO_ENCRYPTED_PASSWORD']
            mongo_key = property_data['MONGO_KEY']

            output, error = subprocess.Popen(
                current_location + '/../../jre/bin/java -jar ' + current_location +
                '/../../properties/Decrypt.jar ' + mongo_encryp_pass + ' ' +
                mongo_key, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT).communicate()
            if error:
                lggr.error("Unable to get the mongo password")
                sys.exit("Unable to get the mongo password")
            output = output.decode().strip('\n')
            mongo_decrypt_pass = output.split(':')[1].strip()
            if not version == '12.0.0':
                instance = self.conf_data['APPVIEWX_SSH'].lower()
                if instance == 'false':
                    db_ip = "localhost"
                    db_port = self.conf_data['APPVIEWX_DB_PORT']
                else:
                    db_ip = self.conf_data['APPVIEWX_DB_PRIMARY_HOST']
                    db_port = self.conf_data['APPVIEWX_DB_PRIMARY_PORT']
            else:
                if "str" in str(type(self.conf_data['MONGODB']['HOSTS'])):
                    db_ip_port = [self.conf_data['MONGODB']['HOSTS']]
                else:
                    db_ip_port = self.conf_data['MONGODB']['HOSTS']
                db_ip, db_port = db_ip_port[0].split(':')
            try:
                client = MongoClient(db_ip, int(db_port), replicaset='rpset')
                if float('.'.join(version.strip('v').split('.')[:-1])) > 10.7:
                    client.admin.authenticate(mongo_username, mongo_decrypt_pass)
            except Exception as e:
                lggr.error("Unable to connect to Database")
                sys.exit("Unable to connect to Database")

            return client
        except Exception as e:
            lggr.error("Unable to get the Mongo Object")
            sys.exit(e)

    def role_check(self, role_db):
        """."""
        try:
            role_with_regex = role_db.find({"accessControlObjects.regexList": {'$exists':True}})
            if role_with_regex.count() > 0:
                return 'Success'
            else:
                return 'Fail'
        except Exception as e:
            lggr.error("Unable to check the role schema")
            sys.exit(e)

    def app_settings_auth(self, appsettings):
        """."""
        try:
            auth = dict()
            for doc in appsettings.find({"subCategory": "LDAP"}):
                auth['ldap'] = doc['properties']
                if len(doc['properties']) == 0:
                    auth['ldap'] = False
            for doc in appsettings.find({"subCategory": "TACACS"}):
                auth['tacacs'] = doc['properties']
                if len(doc['properties']) == 0:
                    auth['tacacs'] = False

            for doc in appsettings.find({"subCategory": "RADIUS"}):
                auth['radius'] = doc['properties']
                if len(doc['properties']) == 0:
                    auth['radius'] = False

            return auth
        except Exception as e:
            lggr.error("Unable to get Auth Settings")
            sys.exit(e)

    def app_settings_provision(self, appsettings):
        """."""
        try:
            provision = dict()
            for doc in appsettings.find({"subCategory": "PROVISIONING"}):
                provision['properties'] = doc['properties']
                if len(doc['properties']) == 0:
                    provision['properties'] = False

            return provision
        except Exception as e:
            lggr.error("Unable to get Provision Settings")
            sys.exit(e)

    def app_settings_ticketing(self, appsettings):
        """."""
        try:
            ticketing = dict()
            ticket_fields = ["TICKET_ENABLED", "TICKETING_POLL_TIME_INTERVAL", "TICKETING_VENDOR_TIMEZONE", "TICKETING_POLL_ENABLED", "TICKETING_DEVICE_VALIDATION_ENABLED", "APPROVE_TICKET_MODE", "IMPLEMENT_TICKET_MODE", "TICKETING_CONFIGS_TO_PUSH", "TICKETING_LOGS_TO_PUSH", "TICKETING_CLOSE_ENABLED"]
            for doc in appsettings.find({"subCategory": "TICKETING"}):
                ticketing['properties'] = dict()
                for field in ticket_fields:
                    ticketing['properties'][field] = doc['properties'][field]
                    if len(doc['properties']) == 0:
                        ticketing['properties'] = False

            return ticketing

        except Exception as e:
            lggr.error("Unable to get Ticketing Settings")
            sys.exit(e)

    def app_settings_device(self, appsettings):
        """."""
        try:
            device = dict()
            for doc in appsettings.find({"subCategory": "DEVICE"}):
                device['properties'] = doc['properties']
                if len(doc['properties']) == 0:
                    device['properties'] = False

            return device
        except Exception as e:
            lggr.error("Unable to get device Settings")
            sys.exit(e)

    def app_settings_log_forward(self, appsettings):
        """."""
        try:
            log = dict()
            for doc in appsettings.find({"subCategory": "LOGFORWARDING"}):
                log['properties'] = doc['properties']
                if len(doc['properties']) == 0:
                    log['properties'] = False
            return log
        except Exception as e:
            lggr.error("Unable to get log_forward Settings")
            sys.exit(e)

    def app_settings_certificate(self, appsettings):
        """."""
        try:
            certificate = dict()
            for doc in appsettings.find({"subCategory": "CERTIFICATE"}):
                certificate['properties'] = doc['properties']
                if len(doc['properties']) == 0:
                    certificate['properties'] = False
            return certificate
        except Exception as e:
            lggr.error("Unable to get Certificate Settings")
            sys.exit(e)

    def app_settings(self):
        """."""
        try:
            properties = ['Authentication', 'Provisioning', 'Ticketing', 'Device', 'Log_Forwarding','Certificate']
            check_property = dict()
            for prop in properties:
                check_property[prop] = str()
            t_end = time.time() + 60 * 2
            while time.time() < t_end:
                try:
                    client = self.get_mongo_object()
                    break
                except:
                    pass
            appviewx_db = client.appviewx
            app_settings = appviewx_db.appSettings
            for prop in check_property:
                if "Authentication" in prop:
                    check_property[prop] = self.app_settings_auth(app_settings)
                elif "Provisioning" in prop:
                    check_property[prop] = self.app_settings_provision(app_settings)
                elif "Ticketing" in prop:
                    check_property[prop] = self.app_settings_ticketing(app_settings)
                elif "Device" in prop:
                    check_property[prop] = self.app_settings_device(app_settings)
                elif "Log_Forwarding" in prop or "Certificate" in prop:
                    check_property[prop] = self.app_settings_log_forward(app_settings)
            return check_property
        except Exception as e:
            lggr.error("Unable to get Consolidate Settings")
            sys.exit(e)

    def schema_change(self):
        """."""
        try:
            collections = ['ROLE']
            check_schema = dict()
            for collection in collections:
                check_schema[collection] = str()
            t_end = time.time() + 60 * 2
            while time.time() < t_end:
                try:
                    client = self.get_mongo_object()
                    break
                except:
                    pass
            appviewx_db = client.appviewx
            role_db = appviewx_db.role
            check_schema['ROLE'] = self.role_check(role_db)

            with open(current_location + '/../../conf/.db_comparison', 'a+') as db_comparison:
                content = db_comparison.read() + '\n\n[SCHEMA CHANGES] \n\n'
                for collection in collections:
                    content = content + '{0:82s}  {1:2s}'.format(collection, check_schema[collection] + "\n\n")
                db_comparison.write(content)
        except Exception as e:
            lggr.error("Unable to get Schema Change")
            sys.exit(e)

    def roles_user_assoc(self, appviewx_db):
        """."""
        try:
            user_db = appviewx_db.user
            users = dict()
            for user in user_db.find():
                user_name = user['loginName']
                users[user_name] = user['roles']
            return users
        except Exception as e:
            lggr.error("Unable to get Role user Association")
            sys.exit(e)

    def get_database_content(self):
        """."""
        try:
            t_end = time.time() + 60 * 2
            while time.time() < t_end:
                try:
                    client = self.get_mongo_object()
                    break
                except:
                    pass
            
            appviewx_db = client.appviewx
            device = appviewx_db.device
            device_count = dict()
            device_category = ['ADC', 'SERVERS', 'DNS', 'FIREWALL', 'SWITCH',
                               'ROUTER', 'OTHERS', 'CLOUD']
            association_category = ['roles_user']
            for category in device_category:
                device_count[category] = 0

            for dev in device.find():
                if dev['category'] == 'ADC':
                    device_count['ADC'] += 1
                elif dev['category'] == 'Server':
                    device_count['SERVERS'] += 1
                elif dev['category'] == 'Firewall':
                    device_count['FIREWALL'] += 1
                elif dev['category'] == 'OTHERS':
                    device_count['OTHERS'] += 1
                elif dev['category'] == 'Switch':
                    device_count['SWITCH'] += 1
                elif dev['category'] == 'Router':
                    device_count['ROUTER'] += 1
                elif dev['category'] == 'Cloud':
                    device_count['CLOUD'] += 1
                elif dev['category'] == 'Dns':
                    device_count['DNS'] += 1
            template_db = appviewx_db.apsTemplates
            alert_db = appviewx_db.alert
            widget_db = appviewx_db.widget
            logging_db = appviewx_db.logging
            template_count = template_db.count()
            role_db = appviewx_db.role
            user_db = appviewx_db.user
            dashboard_db = appviewx_db.dashboard
            credential_store_db = appviewx_db.credentialStore
            role_count = role_db.count()
            user_count = user_db.count()
            consolidate_info = dict()
            consolidate_info['devices'] = device_count
            consolidate_info['dashboard'] = dashboard_db.count()
            consolidate_info['roles'] = role_count
            consolidate_info['credentials_store'] = credential_store_db.count()
            consolidate_info['users'] = user_count
            consolidate_info['templates'] = template_count
            consolidate_info['alert'] = alert_db.count()
            consolidate_info['widget'] = widget_db.count()
            consolidate_info['reports_logs'] = logging_db.count()
            consolidate_info['association'] = dict()
            consolidate_info['settings'] = self.app_settings()
            for assoc in association_category:
                if assoc == 'roles_user':
                    consolidate_info['association']['roles_user'] = dict()
                    roles_user_assoc = self.roles_user_assoc(appviewx_db)
                    consolidate_info['association']['roles_user'] = roles_user_assoc
            database_content = json.dumps(consolidate_info)
            if "pre" in self.time:
                file_name = current_location + "/../../conf/.premigration"
            else:
                file_name = current_location + "/../../conf/.postmigration"

            with open(file_name, 'w+') as db_data:
                db_data.write(database_content)
        except Exception as e:
            lggr.error("Unable to get Database Content")
            sys.exit(e)

    def report_generation(self):
        """."""
        try:
            with open(current_location + '/../../conf/.premigration') as pre:
                pre_content = pre.readlines()[0]
        except Exception:
            lggr.error("Not able to read premigration report")
            sys.exit("Not able to read premigration report")
        try:
            with open(current_location + '/../../conf/.postmigration') as post:
                post_content = post.readlines()[0]
        except:
            lggr.error("Not able to read postmigration report")
            sys.exit("Not able to read postmigration report")
        try:
            pre_json = json.loads(pre_content)
            post_json = json.loads(post_content)
            with open(current_location + '/../../conf/.db_comparision', 'w+') as report:
                report.writelines(
                    '{0:35s}  {1:20s}    {2:20s} {3:1s}'.format("OBJECT", "PRE_MIGRATION", "POST_MIGRATION", "STATUS\n\n\n"))
                for Object in pre_json.keys():
                    if "association" not in Object and 'settings' not in Object:
                        if Object == 'devices':
                            for device in pre_json['devices'].keys():
                                status = "Ok" if pre_json['devices'][device] == \
                                    post_json['devices'][device] else "Not Ok"
                                report.writelines('{0:35s}  {1:20s}      {2:20s} {3:1s}'.format("Inventory[" + device + "]",str(pre_json['devices'][device]), str(post_json['devices'][device]), status + '\n\n'))
                        else:
                            if "users" in str(Object):
                                status = "Ok" if pre_json[Object] == \
                                    post_json[Object] or int(pre_json[Object]) == int(post_json[Object]) - 1 else "Not Ok"
                            elif 'templates' in str(Object):
                                status = "Ok" if pre_json[Object] == \
                                    post_json[Object] or int(pre_json[Object]) == int(post_json[Object]) - 29 else "Not Ok"
                            else:
                                status = "Ok" if pre_json[Object] == \
                                    post_json[Object] else "Not Ok"
                            report.writelines('{0:35s}  {1:20s}      {2:20s} {3:1s}'.format(Object,str(pre_json[Object]), str(post_json[Object]), status + '\n\n'))
        except Exception as e:
            lggr.error("Unable to generate reports for Objects")
            sys.exit(e)
        try:
            with open(current_location + '/../../conf/.db_comparision', 'a+') as report:
                for Object in pre_json.keys():
                    if "settings" not in Object and "association" in Object:
                        report.writelines('\n\n[ASSOCIATION]\n\n')
                        for assoc in pre_json['association']:
                            if "roles_user" in assoc:
                                report.writelines('Roles_User :\n\n')
                                for users in pre_json['association']['roles_user']:
                                    pre_roles = pre_json['association']['roles_user'][users]
                                    try:
                                        post_roles = post_json['association']['roles_user'][users]
                                    except:
                                        post_roles = False
                                        status = "Not ok"
                                    if pre_roles == post_roles:
                                        status = "Ok"
                                    else:
                                        status = "Not Ok"
                                    report.writelines('{0:82s}  {1:1s}'.format(users, status + "\n\n"))
        except Exception as e:
            lggr.error("Unable to generate reports for Association")
            sys.exit(e)
        try:
            with open(current_location + '/../../conf/.db_comparision', 'a+') as report:
                for Object in pre_json.keys():
                    if "settings" in Object and "association" not in Object:
                        report.writelines('\n\n[SETTINGS]\n\n')
                        for assoc in pre_json['settings']:
                            defect_list = list()
                            for prop in pre_json['settings'][assoc]:
                                try:
                                    if pre_json['settings'][assoc][prop] == post_json['settings'][assoc][prop]:
                                        status = "Ok"
                                    else:
                                        defect = assoc if "Authentication" not in assoc else prop
                                        defect_list.append(defect)
                                except:
                                    status = "Not Ok"
                            if len(defect_list) > 0:
                                status = "Not Ok [ " + ",".join(defect_list).strip(',') + "]"
                            report.writelines('{0:82s}  {1:1s}'.format(assoc, status+'\n\n'))
        except Exception as e:
            lggr.error("Unable to generate reports for Settings")
            sys.exit(e)



    def file_send(self):
        """."""
        """
        current_ip = socket.gethostbyname(socket.gethostname())
        web_ips = self.conf_data['WEB']['HOSTS']
        if "str" in str(type(web_ips)):
            web_ips = [web_ips]
        for web_ip in web_ips:
            ip, port = web_ip.split(':')
            if  not ip == current_ip or 'localhost' in ip
            username, path = self.get_username_path(ip)
                cmd = "scp " + current_location + "/../../conf/.db_comparison " + username + "@" + ip + "/" + path + "/web/apache-tomcat-web/webapps/AppViewXNGWeb/" 
                output, error = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()
                if error:
                    sys.exit("Unable to send the migration report to " + ip)
        """
        try:
            from using_fabric import AppviewxShell
            from config_parser import config_parser
            location = os.path.realpath(
                os.path.join(os.path.dirname(__file__), "../../conf"))
            conf_data = config_parser(location + '/appviewx.conf')
            ips = conf_data['WEB']['ips']
            from avx_commons import get_username_path
            for ip in ips:
                    user, path = get_username_path(conf_data, ip)
                    f_ob = AppviewxShell([ip], user=user)
                    f_ob.file_send(location + '/.db_comparision',
                                   path + '/web/apache-tomcat-web/webapps/AppViewXNGWeb/MigrationStatus')
        except Exception as e:
            lggr.error("Unable to Send the Final Report to Final Location")
            sys.exit(e)

    def initialize(self):
        """."""
        self.get_database_content()
        self.report_generation()
        self.file_send()

if __name__ == "__main__":
    args = sys.argv[1:]
    check_obj = DBMIGRATIONCHECK(args[0], args[1])
    if "pre" in args[0]:
        check_obj.get_database_content()
    else:
        check_obj.initialize()
