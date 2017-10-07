#!../Python/bin/python
import set_path
import psutil
import subprocess
import time
import warnings
import set_path
import traceback
import socket
from termcolor import colored
from pymongo import MongoReplicaSetClient
import sys
import os
import requests
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import paramiko
from configobj import ConfigObj
import logger
lggr = logger.avx_logger('avx_commons')
ssh_node = paramiko.SSHClient()
ssh_node.set_missing_host_key_policy(paramiko.AutoAddPolicy())
avx_path = set_path.AVXComponentPathSetting()
warnings.filterwarnings("ignore")
where_am_i = os.path.dirname(os.path.realpath(__file__)) + "/../"
passwords_nodes = dict()


def component_help_fun(component):
    """help_fun display text to guide user in case of invalid arguments given by user or upon request."""
    if component == "plugins":
        comp_arg = "[plugin_name]"
    else:
        comp_arg = "<ip_address>"
    print (""" \n    usage: ./appviewx [option] """ + component + """ [component-arg] \n \
   basic options:\n \
     \t --start \t \t start the  """ + component + """  \n \
     \t --stop \t \t stop the  """ + component + """ \n  \
     \t --status \t \t status of the  """ + component + """ \n \
     \t --restart \t \t restart the  """ + component + """ \n \
     \t --help \t \t show this usage  """ + component + """ \n \
   [component-arg] :
     \n \
     \t""" + comp_arg + """
   example: "\n \
     \t 1. appviewx --start """ + component + """ """ + comp_arg + """ \n \

""")
    sys.exit(1)


def sigint_handler(signal, frame):
    """."""
    print('Keyboard Interrupt!')
    sys.exit(1)


def help_fun(component, operation):
    """."""
    print(" ERROR in user_input:")
    print(" \t\t 1) ./appviewx  %s %s" % (operation, component))
    print(" \t\t 2) ./appviewx  %s %s <ip>" % (operation,component))
    print(" \t\t 2) ./appviewx  %s %s <ip> <port>" % (operation,component))
    sys.exit(1)


def print_statement(
        comp, version, ip, port, primary_status, secondary_status=''):
    """Function to print statement."""
    primary_status = primary_status.lower()
    secondary_status = secondary_status.lower()
    if comp.lower() == 'database':
        comp = 'avx_platform_database'
    elif comp.lower() == 'gateway':
        comp = 'avx_platform_gateway'
    elif comp.lower() == 'web':
        comp = 'avx_platform_web'
    if primary_status in ['started', 'starting'] or primary_status == 'running':
        primary_color = 'green'
    elif primary_status == 'stopped' or primary_status == 'not running':
        primary_color = 'red'
    else:
        primary_color = 'yellow'

    if secondary_status in ['started', 'starting'] or secondary_status == 'running':
        secondary_color = 'green'
    elif secondary_status == 'stopped' or secondary_status == 'not running':
        secondary_color = 'red'
    elif secondary_status == 'vip':
        secondary_color = 'blue'
    else:
        secondary_color = 'yellow'

    if len(comp) > 25:
        comp = comp[:22] + '...'
    if version:
        version = '[' + version + ']'
    version_color = 'blue'

    primary_status = ' '.join(
        [x.capitalize() for x in primary_status.strip().split()])

    if secondary_status:
        secondary_status = ' '.join(
            [x.capitalize() for x in secondary_status.strip().split()])
        secondary_status = '[' + secondary_status + ']'

    print(
        '{0:25s}  {1:25s}  {2:15s}  {3:7s}    {4:15s}  {5:25s}'.format(
            comp, colored(version, version_color), ip, port,
            colored(primary_status, primary_color), colored(
                secondary_status, secondary_color)))


def get_node_details(conf_data, installation_type, user_input):
    """
    get_node_details return node_details list which
    contains node details with username@ip:path format
    """
    try:
        lggr.debug('inside get_node_details()')
        node_details = []
        if installation_type is "singlenode":
            lggr.debug('singlenode')
            hostname = socket.gethostbyname(socket.gethostname())
            where_am_i = os.path.dirname(os.path.realpath(__file__)) + "/../"
            lggr.debug('importing getpass module')
            import getpass
            lggr.debug('fetching user name')
            username = getpass.getuser()
            ip = hostname
            path = where_am_i
            details = username + '@' + ip + ':' + path
            lggr.debug('appending node details to variable node_details')
            node_details.append(details)
        else:
            lggr.debug('multinode')
            usernames = conf_data['credentials']['username']
            if not user_input == 'all':
                ip_index = conf_data['credentials']['nodes'].index(user_input)
                path = conf_data['credentials']['paths'][ip_index]
                if len(usernames) > 1:
                    username = usernames[ip_index]
                else:
                    username = usernames[0]
                details = username + '@' + user_input + ':' + path
                node_details.append(details)
            else:
                if len(usernames) > 1:
                    for ip, path, username in zip(
                            conf_data['credentials']['nodes'],
                            conf_data['credentials']['paths'],
                            conf_data['credentials']['username']):
                        details = username + '@' + ip + ':' + path
                        node_details.append(details)
                else:
                    username = usernames[0]
                    for ip, path in zip(
                            conf_data['credentials']['nodes'],
                            conf_data['credentials']['paths']):
                        details = username + '@' + ip + ':' + path
                        node_details.append(details)
        lggr.debug('returning from get_node_details()')
        return node_details
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def return_status_message_fabric(fabric_obj):
    """The method returns the status and message from a fabric object."""
    key, value = fabric_obj
    status = list(value)[-1][-1]
    res = list(value)[-1][0]
    lggr.debug(res, status)
    return status, res


def check_accessibility(node_details, conf_data):
    """."""
    try:
        hostname = socket.gethostbyname(socket.gethostname())
        for node in node_details:
            if hostname in node:
                continue
            conn_port = conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(node.split('@')[1])] 
            conn_port = str(conn_port)
            check_state = subprocess.run(
                'ssh -q -oStrictHostKeyChecking=no -p %s -w 1 -o ConnectTimeout=5 %s "echo 2>&1" && echo "OK" || echo "NOK" > /dev/null 2>&1' %
                (conn_port, node), shell=True, stdout=subprocess.PIPE)
            result = check_state.stdout.decode()
            if result.strip() == 'OK':
                return True
            if not result.strip() == 'OK':
                print('Node:%s is unreachable' % node.split('@')[1])
                return False
                # sys.exit(1)
            return True
    except KeyboardInterrupt:
        print(colored('Keyboard Interrupt', 'red'))
        sys.exit(1)
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)


def connect_node(ip, username, password=None):
    """Connect to other nodes."""
    try:
        from config_parser import config_parser
        conf_file = where_am_i + '../conf/appviewx.conf'
        conf_data = config_parser(conf_file)
        conn_port = 22
        try:
            conn_port = int(conf_data['ENVIRONMENT']['ssh_port'][conf_data['ENVIRONMENT']['ips'].index(ip)])
        except Exception:
            pass
        if not password:
            try:
                ssh_node.connect(ip, username=username, timeout=3, port=conn_port)
            except:
                ssh_node.close()
                if ip not in passwords_nodes.keys():
                    import getpass
                    passwords_nodes[ip] = getpass.getpass("password for node " + ip + ":")
                ssh_node.connect(ip, username=username, password=passwords_nodes[ip], port=conn_port)
        else:
            ssh_node.connect(ip, username=username, password=password, port=conn_port)
        return ssh_node
    except KeyboardInterrupt:
        print(colored('Keyboard Interrupt', 'red'))
        sys.exit(1)
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)


def execute_on_particular_ip(conf_data, ip, cmd):
    """."""
    try:
        import using_fabric
        user, path = get_username_path(conf_data, ip)
        command = using_fabric.AppviewxShell([ip], user=user)
        f_obj = command.run(cmd)
        status, res = return_status_message_fabric(f_obj)
        if not status:
            lggr.error('Unable to execute command: ' + cmd + ' on: ' + ip)
    except KeyboardInterrupt:
        sys.exit(1)


def replica_set(path, conf_data, primary_ip=''):
    """
    replica_set function will
    set mongo replica
    """
    try:
        #   Replica set name
        replica_set_name = "rpset"

        # File Name
        replica_file = path + 'scripts/replica_set_conf.js'

        # mongo
        mongo_home = path + 'db/mongodb/'
        mongo = mongo_home + 'bin/mongo'

        replica_initiate = {
            "replSetInitiate": {
                "_id": replica_set_name,
                "members": []}}
        try:
            db_details_object, _ = get_db_details(conf_data)
            db_details = [i for i in db_details_object]
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            lggr.error(e)
            print("Couldnt fetch db details for replica set. terminating")
            sys.exit(1)
        for idx, db in enumerate(db_details, start=1):
            db_host_port = db[0] + ':' + db[1]
            if db[0] in conf_data['MONGODB']['arbiter_hosts']:
                db_value = {
                    "_id": idx,
                    "host": db_host_port,
                    "arbiterOnly": "true"}
            else:
                db_value = {"_id": idx, "host": db_host_port}
            replica_initiate["replSetInitiate"]["members"].append(db_value)
        db_run_cmd = "db.runCommand(" + str(replica_initiate) + ")"
        lggr.debug(' creating temp file with name replica_set_conf.js ')
        lggr.debug(db_run_cmd)
        insert_to_file = open(replica_file, 'w')
        insert_to_file.write(db_run_cmd)
        lggr.debug('writing into file replica_set_conf')
        insert_to_file.close()
        replica_cmd = mongo + ' ' + db_details[0][0] + ':' + db_details[0][1] + '/admin --quiet ' + replica_file
        lggr.debug(' running command for replica set')
        try:
            import subprocess
            import os
            ps = subprocess.Popen(
                replica_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            ps.stdout.close()
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            lggr.error(replica_cmd)
            lggr.error(e)
            print("Couldnt complete replica set ")
        lggr.debug('removing temp. file replica_set_conf.js')
        try:
            os.remove(replica_file)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print("Couldnt remove temporary file replica_set_conf.js")
            lggr.error(e)
        lggr.debug('returning from replica_set()')
        return True
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        lggr.error(e)
        sys.exit(1)


def process_status(req_page,response_data=False):
    """."""
    try:
        response = requests.get(req_page,timeout=10,verify=False)
        if response.status_code == 200:
            response_code="pageUp"
        else:
            response_code="pageDown"
        if response_data:
           return response_code,response
        return response_code
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        if response_data:
           return "pageDown",''
        return "pageDown"

def get_heap_size(plugin,h_type='min'):
    try:
        plugin_path = plugin
        if os.path.isdir(avx_path.plugin_path + plugin_path):
            if os.path.isfile(avx_path.plugin_path + plugin_path + "/" + plugin + '.conf'):
                plugin_conf_data = ConfigObj(avx_path.plugin_path + plugin_path + "/" + plugin + '.conf')
                try:
                    if h_type=='min':
                       heap_size = plugin_conf_data['HEAP_MIN']
                    elif h_type=='max':
                       heap_size = plugin_conf_data['HEAP_MAX']
                except KeyboardInterrupt:
                    print('Keyboard Interrupt')
                    sys.exit(1)
                except Exception:
                    lggr.error("HEAP_SIZE field is not found in %s.conf file" % plugin)
                    raise Exception
                return heap_size
    except Exception:
         raise Exception


def get_plugin_version(plugin):
    try:
        plugin_conf_file = avx_path.plugin_path + '/' + plugin + '/' + plugin + '.conf'
        conf_data = ConfigObj(plugin_conf_file)
        try:
            version = conf_data['VERSION']
        except:
            version = conf_data['version']
        return 'v' + version
    except:
        return '-'


def jar_name(plugin,container_id=False):
    """."""
    try:
        plugin_path = plugin
        if os.path.isdir(avx_path.plugin_path + plugin_path):
            if os.path.isfile(avx_path.plugin_path + plugin_path + "/" + plugin + '.conf'):
                vm_type = ''
                plugin_conf_data = ConfigObj(avx_path.plugin_path + plugin_path + "/" + plugin + '.conf')
                if container_id:
                   try:
                      container_id = plugin_conf_data['CONTAINER_ID']
                      return container_id
                   except KeyboardInterrupt:
                     raise Exception
                try:
                    vm_type = plugin_conf_data['CATEGORY']
                except KeyboardInterrupt:
                    print('Keyboard Interrupt')
                    sys.exit(1)
                except Exception:
                    print(colored("CATEGORY field is not found in %s.conf file" % plugin,"red"))
                    lggr.error("CATEGORY field is not found in %s.conf file" % plugin)
                    raise Exception
                try:
                    parameter = plugin_conf_data['PARAMETER']
                except KeyboardInterrupt:
                    print('Keyboard Interrupt')
                    sys.exit(1)
                except Exception:
                    parameter = ''
                return vm_type,parameter
            else:
                print(colored("%s.conf file is missing in %s folder" % (plugin,avx_path.plugin_path + plugin_path),"red"))
                lggr.error("%s.conf file is missing in %s folder" % (plugin,avx_path.plugin_path + plugin_path))
                raise IOError
        else:
            print(colored("%s directory is missing in plugins folder" % plugin,"red")) 
            lggr.error("%s directory is missing in plugins folder")
            raise FileNotFoundError
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        raise Exception

def get_datacenter(conf_data, ip):
    """."""
    datacenter = ''
    try:
        for index in range(0, len(conf_data['ENVIRONMENT']['datacenter'])):
            if ip in conf_data['ENVIRONMENT']['datacenter'][index]:
                datacenter = conf_data['ENVIRONMENT'][
                    'datacenter'][index].split(':')[0]
        if datacenter == '':
            raise Exception
        return datacenter
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        raise Exception


def kill_process(process_id):
    """kill_process is to kill specific process with an id.
        kill_process function is been called from other functions

    Args:
      process_id in string format - on executing gets process id

    """
    try:
        ps = subprocess.Popen(
            process_id,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        ps.stdout.close()
        output = output.decode("utf-8").split('\n')
        for ps_id in output[::-1]:
            kill_cmd = "kill -9 " + ps_id.strip('\n')
            ps_kill = subprocess.Popen(
                kill_cmd, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output = ps_kill.communicate()[0]
            ps_kill.stdout.close()
        return True
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        sys.exit(1)


def kill_proc_by_name(process_name):
    for proc in psutil.process_iter():
        if proc.name == process_name:
            proc.kill()


def get_username_path(conf_data, ip):

    try:
        host_details = conf_data['ENVIRONMENT']['ssh_hosts']
        for host_detail in host_details:
            username, data = host_detail.split('@')
            host_ip, path = data.split(':')
            if ip == host_ip:
                if not path.endswith("/"):
                    path = path + "/"
                return username, path
        raise Exception
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        print(e)


def mongo_status(ip, port, authentication=None):
    '''
    mongo_status is to check status of mongodb
    on a node. will return mongo status list
    '''
    try:
        from pymongo import MongoClient, uri_parser
        mongodb_stat = []
        if not authentication:
            uri = 'mongodb://' + ip + ':' + port
        else:
            db_username, db_password, db_name = get_db_credentials()
            uri = 'mongodb://' + db_username + ':' + db_password + '@' + ip + ':' + port
        try:
            conn = MongoClient(uri)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception:
            mongodb_stat.append('not_running')
            return mongodb_stat
        db = conn['admin']
        if authentication:
            parsed = uri_parser.parse_uri(uri)
            db.authenticate(parsed['username'], parsed['password'])
        else:
            parsed = uri_parser.parse_uri(uri)
        try:
            db.command('serverStatus')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            mongodb_stat.append('not_running')
            return mongodb_stat
        try:
            db.command('serverStatus')['repl']['primary']
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception:
            mongodb_stat.append('no_primary')
        db.command('dbstats')
        try:
            replica_data = db.command('replSetGetStatus')
            if 'syncing to' in replica_data or 'initial sync need' in replica_data or 'still initializing' in replica_data or "infoMessage" in replica_data[
                    'members'][0].keys():
                mongodb_stat.append('no_replication')
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except:
            mongodb_stat.append('no_replication')
        conn.server_info()
        mongodb_stat.append('running')
        return mongodb_stat
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        sys.exit(1)


def run_local_cmd(cmd):
    """The function is used to execute a shell command."""
    try:
        ps = subprocess.run(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        ret_code = ps.returncode
        out = ps.stdout.decode()
        err = ps.stderr.decode()
        return ps
    except Exception as e:
        print(e)
        lggr.error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
    if ret_code:
        lggr.error('Error in executing command: ' + cmd)
        lggr.error('Error: ' + err)
    else:
        lggr.debug('Successfully executed command: ' + cmd)
        lggr.debug('Output: ' + out)


def port_status(ip, port):
    """."""
    try:
        if port == ' ':
            return 'not_available'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        try:
            result = sock.connect_ex((ip, int(port)))  # socket connection
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            return "not_reachable"
        sock.close()
        if result == 0:  # result from socket connection
            return "listening"
        else:
            return "open"
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        sys.exit(1)

def udp_port_status(ip, port):
    """."""
    try:
        if port == ' ':
            return 'not_available'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(15)
        try:
            result = sock.connect_ex((ip, int(port)))  # socket connection
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            return "not_reachable"
        sock.close()
        if result == 0:  # result from socket connection
            return "listening"
        else:
            return "open"
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        sys.exit(1)

def get_decrypt_jar():
    '''
    path for decrypt jar which is used to decrypt the password

    '''
    try:
        decrypt_jar_path = where_am_i + '/../properties/Decrypt.jar'
        if os.path.exists(str(decrypt_jar_path)):
            return decrypt_jar_path
        else:
            print("Could not locate decrypt jar @ %s" % decrypt_jar_path)
            sys.exit(1)
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        sys.exit(1)


def primary_db(conf_data, status=False):
    '''
     Check single node/multinode and get the primarydb
    '''
    try:
        # get db details and instance (single node or multinode)
        db_details, instance = get_db_details(conf_data)
        db_primary = db_connect(db_details, instance, status)
        return db_primary
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        sys.exit(1)


def db_connection(conf_data, status):
    '''
    Connect to mongo replicaSet. Mongo authentication is yet to be done

    '''
    host = primary_db(conf_data, status)
    try:
        # get db details
        db_username, db_password, db_name = get_db_credentials()
        # connect to db
        connect_db = MongoReplicaSetClient(host, replicaSet='rpset')
        connect_db.admin.authenticate(db_username, db_password, source=db_name)
        return connect_db
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        raise Exception


def decrypt(encryptedpassword, key):
    '''
     module to decrypt an EncryptedPassword

    '''
    try:
        import subprocess
        decrypt_jar_path = get_decrypt_jar()
        java_path = where_am_i + '/../jre/bin/java'
        cmd = java_path + ' -jar ' +\
            decrypt_jar_path + ' ' + encryptedpassword + ' ' + key
        # run cli cmd to decrypt jar
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        result = stdout.decode("utf-8")
        if 'Could not reserve enough space for object heap' in result:
           print (colored('Insufficient RAM to proceed it','red'))
           sys.exit(1)
        password = ((result.strip('\n')).split(':')[1]).strip()
        return password
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        sys.exit(1)


def get_mongo_username_path(conf_data, ip):

    try:
        if not conf_data['MONGODB']['mongo_separate_user'][0].lower() == 'true':
           username,path = get_username_path(conf_data, ip)
           return username,path
        host_details = conf_data['MONGODB']['mongo_user']
        for host_detail in host_details:
            username, data = host_detail.split('@')
            host_ip, path = data.split(':')
            if ip == host_ip:
                if not path.endswith("/"):
                    path = path + "/"
                return username, path
        raise Exception
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        print(e)




def get_db_credentials():
    '''
    module to get DB credentials such as
        username, password, and DB name
    '''
    try:
        from configobj import ConfigObj, ConfigObjError
        appviewx_properties_file = where_am_i + '/../properties/appviewx.properties'
        try:
            appviewx_properties = ConfigObj(appviewx_properties_file)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except (ConfigObjError, IOError) as e:
            if 'MICROSOFT_AGENT_ADDRESS:' in e.message:
                sed_avx_prop = "sed -i -e 's/MICROSOFT_AGENT_ADDRESS:/MICROSOFT_AGENT_ADDRESS=/g' " + appviewx_properties_file
                run_local_cmd(sed_avx_prop)
                sed_template_avx_prop = "sed -i -e 's/MICROSOFT_AGENT_ADDRESS:/MICROSOFT_AGENT_ADDRESS=/g' " + \
                    path + "/../properties/templates/template_appviewx_properties"
                run_local_cmd(sed_template_avx_prop)
            else:
                sys.exit(1)
        appviewx_properties = ConfigObj(appviewx_properties_file)
        db_encryptedpassword = appviewx_properties['MONGO_ENCRYPTED_PASSWORD']
        # get encrpted password from appviewx.properties file
        db_key = appviewx_properties['MONGO_KEY']
        # db username from appviewx.properties
        db_username = appviewx_properties['MONGO_USERNAME']
        # db name from appviewx.properties
        db_name = appviewx_properties['MONGO_AUTHENTICATION_DB']
        db_password = decrypt(db_encryptedpassword, db_key)
        return db_username, db_password, db_name
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


def get_db_details(conf_data):
    '''
    module to get DB details and instance
    (single node / multinode)
    '''
    try:
        db_ips = conf_data['MONGODB']['ips']
        db_ports = conf_data['MONGODB']['ports']
        instance = conf_data['ENVIRONMENT']['multinode'][0]
        db_details = zip(db_ips, db_ports)
        return db_details, instance
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception:
        raise Exception


def db_connect(db_details, instance, status=False):
    """
    db_connect function returns primary db ip and its port
    """
    if instance.lower() == 'true':
        try:
            from pymongo import MongoReplicaSetClient
            try:
                db_username, db_password, db_name = get_db_credentials()
                db_list = list()
                for db in db_details:
                    db_list.append(db[0] + ':' + db[1])
                cmd = ','.join(db_list)
                c = MongoReplicaSetClient(cmd, replicaSet='rpset')
                try:
                    c.admin.authenticate(
                        db_username, db_password, source=db_name)
                except Exception:
                    lggr.debug("MongoReplicaSetClient connected without authentication")
                time.sleep(2)
                if not status:
                    time.sleep(20)
                primary_db_machine = c.primary
                c.close()
                db_host = str(primary_db_machine[
                              0]) + ':' + str(primary_db_machine[1])
            except Exception:
                print("Couldnt fetch primary db details. terminating")
                sys.exit(1)
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception:
            print(colored('\n Couldnt able to connect to database ', "red"))
            sys.exit(1)
    else:
        try:
            for db_hosts in db_details:
                db_host = str(db_hosts[0]) + ':' + str(db_hosts[1])
        except KeyboardInterrupt:
            print('Keyboard Interrupt')
            sys.exit(1)
        except Exception as e:
            print(colored('\n Couldnt able to connect to database ', "red"))
            sys.exit(1)
    return db_host
