#!../../Python/bin/python
import os
from avx_commons import run_local_cmd
try:
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    egg_cache_dir = os.path.join(current_file_path + '/.python_egg_cache')
    if not os.path.exists(egg_cache_dir):
        os.makedirs(egg_cache_dir)
    run_local_cmd('chmod g-wx,o-wx ' + egg_cache_dir)
    os.environ['PYTHON_EGG_CACHE'] = egg_cache_dir
except Exception:
    pass
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import sys
import socket
import getpass
import inspect
import logging
import traceback
from configobj import ConfigObj
import logger
lggr = logger.avx_logger('Loadbalancer')
hostname = socket.gethostbyname(socket.gethostname())
current_username = getpass.getuser()
current_file = inspect.getfile(inspect.currentframe())
position = current_username + '@' + hostname + '-' + current_file


where_am_i = os.path.dirname(os.path.realpath(__file__))

appviewx_dir = where_am_i.split('scripts')[0]


def get_container_id(path):
    """writting this function kepping in mind that it will be present
     in commons"""
    path = path + "/../../Plugins"
    container_ids = []
    from config_parser import config_parser
    conf_data = config_parser(where_am_i + '/../../conf/appviewx.conf') 
    plugins = conf_data['PLUGINS']['enabled_plugins'][0].split(',')
    for i in plugins:
        if os.path.isdir(path + "/" + i):
            internal_path = path + "/" + i + "/"
            internal_dir = os.listdir(internal_path)
            for j in internal_dir:
                container = ""
                version = ""
                jar = None
                if j.endswith(".conf"):
                    conf_file = open(internal_path + "/" + j)
                    conf_content = conf_file.readlines()
                    for x in conf_content:
                        if not x.startswith("#"):
                            if "VERSION" in x:
                                version = str(x.split("=")[1]).strip("\n")

                            elif "CONTAINER_ID" in x:
                                container = str(x.split("=")[1]).strip("\n")
                        
                    container_ids.append((i, version, container, i))
             
    return container_ids


def get_gateway_ip_port(
        conf_data,
        hosts,
        ports,
        container_id='gateway',
        version=None):
    try:
        if len(hosts):
            data = '''db.loadBalancer.save({ "_id" : "''' + str(container_id) + '''", "container_id" :"''' + str(container_id) + '''" ,"default_datacenter":"''' + str(
                    conf_data['ENVIRONMENT']['default_datacenter'][0]) + '''","last_used_global_index" :-1, "data_centers" : ['''
            if conf_data['ENVIRONMENT']['multinode'][0].upper() == 'TRUE':
                for dc in conf_data['ENVIRONMENT']['datacenter']:
                    key, value = dc.split(":")
                    collection_data = '{"datacenter_name" :"' + \
                        key + '","last_used_index" : -1,"nodes" : ['
                    counter = 0
                    data_temp = ''
                    for ip, port in zip(hosts, ports):

                        name = get_datacenter(conf_data, ip)

                        if name == key:

                            iagent = '''{ "name" : " ", "ip_port" : "''' + ip + ''':''' + port + '''"},'''
                            data_temp = data_temp + iagent
                            counter = counter + 1
                    if counter:
                        data = data + collection_data
                        data = data + data_temp
                        data = data[:-1]
                        data = data + ']},'
                data = data[:-1]
            else:
                data = data + '''{"datacenter_name" :"''' + str(conf_data['ENVIRONMENT'][
                                                                'default_datacenter'][0]) + '''","last_used_index" : -1,"nodes" : ['''
                gateway = ''
                for i in range(0, len(hosts)):
                    gateway = gateway + '''{ "name" : " ", "ip_port" : "''' + hosts[
                        i] + ''':''' + ports[i] + '''"},'''
                data = data + gateway[:-1]
                data = data + ']}'
            data = data + '] });\n'
            return data
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error(e)
        sys.exit(1)


def gateway_js(plugins):
    """
    Things to be fixed:
        In this script we are hard coding the plugins of statistics which are not to be removed during initializing    
    """

    try:

        from config_parser import config_parser
        conf_data = config_parser(where_am_i + '/../../conf/appviewx.conf')
        name = where_am_i + '/gateway_loalbalancer.js'
        data = ''

        with open(name, 'w') as create_file:
         create_file.write(data)
         for plugin, version, container_id, jar in plugins:
            if jar.split(".")[0] in conf_data['PLUGINS']['plugins']:
                plugin_ip = conf_data['PLUGINS'][
                    jar.split(".")[0].lower()]['ips']
                data = get_gateway_ip_port(
                    conf_data, plugin_ip, conf_data['PLUGINS'][
                        jar.split(".")[0]]['ports'], container_id, version)
                create_file.write(data)
        return True
    except Exception as e:
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
        plugins = get_container_id(where_am_i)
        gateway_js(plugins)

    except KeyboardInterrupt:
        print (Bcolors.FAIL + '\n Keyboard Interrupt ' + Bcolors.ENDC)
        lggr.error("Keyboard Interrupt by user")
        sys.exit(1)
    except Exception as e:
        error = ''.join(traceback.format_exception(*sys.exc_info()))
        lggr.error(error)
        lggr.error("Something went wrong; terminating script. the error is : %s " % (e))
        print (e)
        sys.exit(1)
