#!../Python/bin/python
# **************************************************************
##
# Copyright (C), AppViewX, Payoda Technologies
##
# sshkeygen_python script which will create public key
# and share with all nodes
##
# This script should be placed in 'script' folder of AppViewX
##
# V 1.0 / 12 May 2015 / Murad / murad.p@payoda.com
##
##
# **************************************************************

import os
from avx_commons import run_local_cmd
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
try:
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    egg_cache_dir = os.path.join(current_file_path + '/.python_egg_cache')
    if not os.path.exists(egg_cache_dir):
        os.makedirs(egg_cache_dir)
    run_local_cmd('chmod g-wx,o-wx ' + egg_cache_dir)
    os.environ['PYTHON_EGG_CACHE'] = egg_cache_dir
except Exception:
    pass

import sys
from config_parser import config_parser
import socket
import getpass
import inspect
import traceback
from configobj import ConfigObj
hostname = socket.gethostbyname(socket.gethostname())
current_username = getpass.getuser()
current_file = inspect.getfile(inspect.currentframe())
position = current_username + '@' + hostname + '-' + current_file
import logger
lggr = logger.avx_logger('system-components')
where_am_i = os.path.dirname(os.path.realpath(__file__))


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

global detail
global dc_values
dc_values = {}


def __data_center(dc):
    try:
        global detail
        detail = {}
        datacentre_name = dc.split(':')[0]
        datacentre_ips = (dc.split(':')[1]).split(',')
        detail[datacentre_name] = datacentre_ips
        dc_values[datacentre_name] = datacentre_ips
        return detail
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def __ip_to_datacentername(values, searchfor):
    try:
        for k in values:
            for v in values[k]:
                if searchfor in v:
                    return k
        return None
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def datacentername(conf_data_center_details, searchfor):
    try:
        global dc_values
        dc_values = {}
        map(__data_center, conf_data_center_details)
        return __ip_to_datacentername(dc_values, searchfor)
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def datacenterdetails(conf_data_center_details):
    try:
        return map(__data_center, conf_data_center_details)
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def create_js_file():
    '''
    create_js_file() will create new file named 'system_components.js'
    inside current running directory.
    if file already exists then remove its content
    '''
    try:
        name = where_am_i + '/system_components.js'
        create_file = open(name, 'w')   # Trying to create a new file
        create_file.close()
        return True
    except Exception as e:
        print (Bcolors.FAIL)
        print (e)
        print (Bcolors.ENDC)
        lggr.error(e)
        sys.exit(0)  # quit Python


def write_into_js_file(data):
    '''
    write_into_js_file() will append the 'data'
    into system_components.js file
    '''
    try:
        js_file = where_am_i + '/system_components.js'
        with open(js_file, "a") as myfile:
            myfile.write(data)
        return True
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def generate_basic_content():
    '''
    generate_basic_content() will append
    initial lines (static) to system_components.py
    '''
    try:
        data = 'use appviewx;' + '\n'
        write_into_js_file(data)
        return True
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def get_container_id(path):
    """writting this function kepping in mind that it will be present in commons"""

    container_ids = dict()
    path = path + "./../plugins"
    container_ids = {}
    plugins = os.listdir(path)
    for i in plugins:
        internal_path = path + "/" + i + "/"
        internal_dir = os.listdir(internal_path)
        for j in interal_dir:
            if j == "conf":
                conf_file = open(internal_path + "/" + j + "/plugin.conf")
                conf_content = conf_file.readline()
                for i in conf_content:
                    if not i.startswith("#"):
                        if "VERSION" in i:
                            version = str(i.split("=")[1]).strip("\n")

                        elif "CONTAINER_ID" in i:
                            container = str(i.split("=")[1]).strip("\n")

                container_ids[version] = container

    return container_ids


def get_mongo_ip_port(conf_data):
    '''
    get_mongo_ip_port() will return tuple which conatins
    mongo db details
    '''
    try:
        data = '''db.systemcomponents.save({ "_id" : "mongodb", "component_id" : "mongodb", "nodes" : ['''
        if conf_data['ENVIRONMENT']['multinode'][0].upper() == 'TRUE':
            primary_db = '''{ "name" : " ", "ip_port" : "''' + conf_data['MONGODB']['ips'][
                0] + ''':''' + conf_data['MONGODB']['ports'][0] + '''", "last_used": " "}'''
            data = data + primary_db
            for ip, port in zip(
                conf_data['MONGODB']['ips'][
                    1:], conf_data['MONGODB']['ports'][
                    1:]):
                secondary_db = ''',{"name" : " ", "ip_port" : "''' + \
                    ip + ''':''' + port + '''", "last_used": " "}'''
                data = data + secondary_db
        else:
            db = '''{ "name" : " ", "ip_port" : "''' + conf_data['MONGODB']['ips'][
                0] + ''':''' + conf_data['MONGODB']['ports'][0] + '''", "last_used": " "}'''
            data = data + db
        data = data + '] });\n'
        return data
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)





def get_web_ip_port(conf_data):
    '''
    get_web_ip_port() will return tuple which conatins
    web details
    '''
    try:
        data = '''db.systemcomponents.save({ "_id" : "web", "component_id" : "web", "nodes" : ['''
        if conf_data['ENVIRONMENT']['multinode'][0].upper() == 'TRUE':
            for ip, port in zip(
                    conf_data['WEB']['ips'],
                    conf_data['WEB']['ports']):
                web = '''{ "name" : " ", "ip_port" : "''' + ip + \
                    ''':''' + port + '''", "last_used": " "},'''
                data = data + web
            data = data[:-1]
        else:
            web = '''{ "name" : " ", "ip_port" : "''' + conf_data['WEB']['ips'][
                0] + ''':''' + conf_data['WEB']['ports'][0] + '''", "last_used": " "}'''
            data = data + web
        data = data + '] });\n'
        return data
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def get_components():
    '''
    get_components() will fetch appviewx components
    from configuration file. A string is created with
    various components details and writes into js file
    '''
    try:
        conf_data = config_parser(
            str(where_am_i) +
            '/../../conf/appviewx.conf')
        data = get_mongo_ip_port(conf_data)
        data = data + (get_web_ip_port(conf_data))
        write_into_js_file(data)
        return True
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def system_components():
    '''
    system_components() is the main function under
    system_components module. This function will
    call create_js_file(), generate_basic_content()
    and get_components()
    '''
    try:
        create_js_file()
        # generate_basic_content()
        get_components()
        return True
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)




def tenant_creation(conf_data):
    try:
        template = 'db.tenant.save('
        property_file = where_am_i + '/../properties/appviewx.properties'
        property_data = ConfigObj(property_file)
        name = where_am_i + '/tenant_collection.js'
        data = {
            "_id": "test",
            "tenant_name": "test",
            "db_config": {
                "database_hosts": [],
                "username": "appviewx",
                "authentication_db": "admin",
                "max_connections": 20}}
        create_file = open(name, 'w')   # Trying to create a new file
        data['db_config']["database_hosts"].append(
            property_data['DATABASE_HOSTS'])
        data['db_config']["username"] = property_data['MONGO_USERNAME']
        data['db_config']["authentication_db"] = property_data[
            'MONGO_AUTHENTICATION_DB']
        data['db_config']["password"] = property_data[
            'MONGO_ENCRYPTED_PASSWORD']
        data['db_config']["key"] = property_data['MONGO_KEY']
        data = template + str(data) + ')'
        create_file.write(str(data))
        return True
    except Exception as e:
        print (e)
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)

def get_datacenter(conf_data, ip):
    datacenter = ''
    try:
        for index in range(0, len(conf_data['ENVIRONMENT']['datacenter'])):
            if ip in conf_data['ENVIRONMENT']['datacenter'][index]:
                datacenter = conf_data['ENVIRONMENT'][
                    'datacenter'][index].split(':')[0]
        if datacenter == '':
            raise Exception
        return datacenter
    except Exception:
        raise Exception

if __name__ == '__main__':
    try:
        lggr.debug('inside system_components module')
        system_components()
    except KeyboardInterrupt:
        print(Bcolors.FAIL + '\n Keyboard Interrupt ' + Bcolors.ENDC)
        lggr.error("Keyboard Interrupt by user")
        sys.exit(1)
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error("Something went wrong; terminating script. the error is : %s " % (e))
        print (e)
        sys.exit(1)
