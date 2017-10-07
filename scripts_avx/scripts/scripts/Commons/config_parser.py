#!../../Python/bin/python
"""."""
import configparser
import os
import hashlib
import pickle
import re
import sys
import socket
from prettytable import PrettyTable
from termcolor import colored
import getpass
hostname = socket.gethostbyname(socket.gethostname())
current_path = os.path.dirname(os.path.realpath(__file__))
import signal

class Bcolors:
    """."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def ipv4_validation(ip):
    """."""
    if re.match(
        r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$',
            ip):
        return True
    return False


def port_checker(port):
    """To check Whether the port is valid or invalid(It should be int and in range between(0,65535)."""
    try:
        isinstance(int(port), int)
        if int(port) > 65535 or int(port) < 0:
            raise ValueError
        return True
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except ValueError:
        return False


def boolean_check(value):
    """."""
    if value.lower() in ['true', 'false']:
        return True
    return False

def compare_hash(file_name):
    """."""
    try:
        with open(current_path + '/.conf_hash.txt') as file_object:
            original_hash = file_object.read()
        if not len(original_hash) > 0:
            return False
    except Exception as e:
        return False
    
    with open( file_name,'rb') as file_object:
        new_hash = hashlib.md5(file_object.read()).hexdigest()
    if original_hash == new_hash:
        return True
    else:
        return False

def create_hash(conf_file):
    """."""
    current_path = os.path.dirname(os.path.realpath(__file__))
    hash_file = current_path + '/.conf_hash.txt'
    with open(hash_file,'wb') as conf_hash,open(conf_file,'r') as conf:
        conf_hash.write(hashlib.md5(conf.read()).hexdigest())

def read_flag(conf_file):
    """."""
    if os.path.isfile(current_path + '/conf_data.p'):
        if not conf_file:
            conf_file = 'appviewx.conf'
        hash_check = compare_hash(conf_file)
        if hash_check:
            conf_object = open(current_path + '/conf_data.p','rb')
            conf_data = pickle.load(conf_object)
            conf_object.close()
            if hostname in conf_data['ENVIRONMENT']['ips']:
                return False
            else:
                return True

        else:
            return True
        
    else:
        return True


def config_parser(conf_file=None):
    """."""
    conf_file = os.path.abspath(conf_file)
    config = configparser.ConfigParser()
    conf_data = {}
    if not conf_file:
        conf_file = 'appviewx.conf'

    if not os.path.isfile(conf_file):
        print(colored("No such file found : %s" % conf_file, "red"))
        sys.exit(1)

    read_check = read_flag(conf_file)

    if read_check:
        try:
            config.read(conf_file)
        except configparser.DuplicateSectionError as e:
            print(e)
            sys.exit(1)
        except configparser.DuplicateOptionError as e:
            print(e)
            sys.exit(1)
        except configparser.ParsingError as e:
            print(1)
            sys.exit(1)

        conf_invalid_data = []
        boolean_field_check = ['https', 'multinode']
        host_field_format = ['hosts']
        ip_port_format = re.compile(r'\d.*:\d.*')
        username_ip_path_format = re.compile('.+@.+:.+')
        colon = ':'
        port_check = list()
        sections = config.sections()
        for section in sections:
            conf_data[section] = dict()
            for key, value in config.items(section):
                key = key.replace(' ', '')
                value = value.replace(' ', '')
                value = value.replace('localhost', hostname)
                value = value.replace('$(hostname-i)', hostname)
                conf_data[section][key] = list()
                conf_data[section][key].append(value)
                if key.lower() in boolean_field_check:
                    if not boolean_check(value):
                        if section.lower() == 'environment' and key.lower() == 'multinode':
                            print(
                                colored(
                                    "MULTINODE field under ENVIRONMENT section should be either True or False",
                                    "red"))
                            sys.exit(1)
                        cmd = section + ">" + key + "> The value should be either True or False"
                        conf_invalid_data.append(cmd)
                    else:
                        conf_data[section]['multinode'][0] = value
                elif key.lower() == 'datacenter':
                    conf_data[section][key] = list()
                    if conf_data['ENVIRONMENT']['multinode'][0].lower() == 'true':
                     for datacenter in value.split('&&'):
                        conf_data[section][key].append(datacenter)
                    else:
                     try:
                      conf_data[section][key].append(conf_data['ENVIRONMENT']['default_datacenter'][0] + ':' + hostname)
                     except KeyError:
                      print(
                                colored(
                                    "DEFAULT_DATACENTER field under ENVIRONMENT section is missing in conf file" ,
                                    "red"))
                      sys.exit(1)
                elif key.lower() == 'ssh_hosts':
                    try:
                        try:
                            ins_type = conf_data[section]['multinode'][0]
                        except KeyboardInterrupt:
                            print('Keyboard Interrupt')
                            sys.exit(1)
                        except Exception:
                            print(
                                colored(
                                    "MULTINODE field under ENVIRONMENT section is missing in conf file",
                                    "red"))
                            sys.exit(1)
                        if ins_type == '':
                            conf_data[section]['multinode'][0] = 'false'
                    except KeyboardInterrupt:
                        print('Keyboard Interrupt')
                        sys.exit(1)
                    except IndexError:
                        conf_data[section]['multinode'][0] = 'false'
                    except KeyError:
                        conf_data[section]['multinode'] = list()
                        conf_data[section]['multinode'][0] = 'false'
                    conf_data[section]['ips'] = list()
                    conf_data[section]['username'] = list()
                    conf_data[section]['path'] = list()
                    conf_data[section]['ssh_hosts'] = list()
                    if conf_data[section]['multinode'][0].lower() == 'false':
                        conf_data[section]['ssh_hosts'].append(value)
                        if not re.match(username_ip_path_format, value):
                            print(
                                colored(
                                    "SSH_HOST(%s) format(username@ip:path) under ENVIRONMENT section is not valid" %
                                    value,
                                    "red"))
                            sys.exit(1)
                        if len(value.split(',')) == 1:
                            username = value.split('@')[0]
                            ip, path = value.split('@')[1].split(':')
                            username = getpass.getuser()
                            conf_data[section]['ips'].append(ip)
                            conf_data[section]['username'].append(username)
                            avx_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                            if os.path.isfile(avx_path + '/conf/appviewx.conf'):
                                conf_data[section]['path'].append(avx_path)
                            else:
                                conf_data[section]['path'].append(path)
                            conf_data[section][key.lower()][0]= username + '@' + ip +':' + avx_path
                        else:
                            cmd = "SSH_HOST under %s should be contain single value(multinode set as False)" % section
                            print (colored(cmd,"red"))
                            sys.exit(1)
                    else:
                        for values in value.split(','):
                            if not re.match(username_ip_path_format, values):
                                print(
                                    colored(
                                        "SSH_HOST(%s) format(username@ip:path) under ENVIRONMENT section is not valid" %
                                        values, "red"))
                                sys.exit(1)
                            username = values.split('@')[0]
                            ip, path = values.split('@')[1].split(':')
                            if not ipv4_validation(ip):
                                print(
                                    colored(
                                        "SSH_HOST(%s) - (IP format) under ENVIRONMENT section is not valid" %
                                        ip, "red"))
                                sys.exit(1)
                                continue
                            conf_data[section]['ips'].append(ip)
                            conf_data[section]['username'].append(username)
                            conf_data[section]['path'].append(path)
                            conf_data[section]['ssh_hosts'].append(values)
                elif key.lower() =='ssh_port':
                     try:
                        conf_data[section][key.lower()] = list()
                        if not value:
                            conf_data['ENVIRONMENT']['ssh_port'] = ['22']
                        else:
                            for port in value.split(','):
                                conf_data[section][key.lower()].append(port)
                        if not len(conf_data['ENVIRONMENT']['ssh_port']) == len(conf_data['ENVIRONMENT']['username']):
                            conf_data['ENVIRONMENT']['ssh_port'] = conf_data['ENVIRONMENT']['ssh_port'] * len(conf_data['ENVIRONMENT']['username'])
                     except Exception as e:
                        print (e)
                elif key.lower() == 'gateway_timeout':
                    conf_data['GATEWAY']['TIMEOUT'] = value
                elif key.lower() == 'mongo_user':
                    try:
                        if not conf_data['MONGODB']['mongo_separate_user'][0].lower() == 'true':
                           continue
                    except Exception:
                        continue
                    conf_data[section]['mongo_ips'] = list()
                    conf_data[section]['mongo_username'] = list()
                    conf_data[section]['mongo_path'] = list()
                    conf_data[section]['mongo_user'] = list()
                    if conf_data['ENVIRONMENT']['multinode'][0].lower() == 'false':
                       if len(value):
                        conf_data[section]['mongo_user'].append(value)
                        if not re.match(username_ip_path_format, value):
                            print(
                                colored(
                                    "MONGO_USER(%s) format(username@ip:path) under MONGODB section is not valid" %
                                    value,
                                    "red"))
                            sys.exit(1)
                        if len(value.split(',')) == 1:
                            username = value.split('@')[0]
                            ip, path = value.split('@')[1].split(':')
                            conf_data[section]['mongo_ips'].append(ip)
                            conf_data[section]['mongo_username'].append(username)
                            conf_data[section]['mongo_path'].append(path)
                            conf_data[section][key.lower()][0]= username + '@' + ip +':' + path
                        else:
                            cmd = "MONGO_USER under %s should be contain single value(multinode set as False)" % section
                            print (colored(cmd,"red"))
                            sys.exit(1)
                    else:
                        for values in value.split(','):
                           if len(values):
                            if not re.match(username_ip_path_format, values):
                                print(
                                    colored(
                                        "MONGO_USER(%s) format(username@ip:path) under ENVIRONMENT section is not valid" %
                                        values, "red"))
                                sys.exit(1)
                            username = values.split('@')[0]
                            ip, path = values.split('@')[1].split(':')
                            if not ipv4_validation(ip):
                                print(
                                    colored(
                                        "MONGO_USER(%s) - (IP format) under ENVIRONMENT section is not valid" %
                                        ip, "red"))
                                sys.exit(1)
                                continue
                            conf_data[section]['mongo_ips'].append(ip)
                            conf_data[section]['mongo_username'].append(username)
                            conf_data[section]['mongo_path'].append(path)
                            conf_data[section]['mongo_user'].append(values)
                if section.lower() == 'plugins':
                    if key.lower() == 'enabled_plugins':
                         conf_data[section]['plugins'] = list()
                         conf_data[section]['plugins'] = value.split(',')
                        #conf_data[section]['folders'] = list()
                        #conf_data[section]['plugins'] = list()
                        #conf_data[section][key.lower()] = list()
                        #for values in value.split(','):
                        #   conf_data[section][key.lower()].append(values)
                        #    if not len(values.split(':')) == 2:
                        #        cmd = section + ">" + key + \
                        #            "> The folder:plugin_name(%s) format is not valid" % values
                        #        conf_invalid_data.append(cmd)
                        #    else:
                        #        folder, plugin = values.split(':')
                        #        conf_data[section]['folders'].append(folder)
                        #        conf_data[section]['plugins'].append(plugin)
                    elif not key.lower() == 'enabled_plugins':
                        conf_data[section][key.lower()] = dict()
                        conf_data[section][key.lower()]['hosts'] = list()
                        conf_data[section][key.lower()]['ips'] = list()
                        conf_data[section][key.lower()]['ports'] = list()
                        conf_data[section][key.lower()]['hosts'] = value.split(',')
                        for data in value.split(','):
                            if not re.match(ip_port_format, data):
                                cmd = section + ">" + key + \
                                    "> The ip:port(%s) format is not valid" % data
                                conf_invalid_data.append(cmd)
                                continue
                            else:
                                if not len(data.split(":")) == 2:
                                    cmd = section + ">" + key + \
                                        "> The ip:port (%s) format is not valid" % ip
                                    conf_invalid_data.append(cmd)
                                    continue
                                ip, port = data.split(colon)
                                if ip not in conf_data['ENVIRONMENT']['ips']:
                                    cmd = section + ">" + key + \
                                        "> The ip (%s) is not present in SSH_HOST field" % ip
                                    conf_invalid_data.append(cmd)
                                    continue
                                if not port_checker(port):
                                    cmd = section + ">" + key + \
                                        "> The port (%s) value is not valid(It should be between 0 and 65535)" % port
                                    conf_invalid_data.append(cmd)
                                    continue
                            port_check.append(data)
                            conf_data[section][
                                key.lower()]['ips'].append(
                                data.split(colon)[0])
                            conf_data[section][
                                key.lower()]['ports'].append(
                                data.split(colon)[1])
                if key.lower() in host_field_format or key.lower() == 'vip_hosts' and conf_data[
                        'ENVIRONMENT']['multinode'][0].lower() == 'true':
                    try:
                        if len(conf_data['ENVIRONMENT']['ips']) == 0:
                            print(
                                colored(
                                    "SSH_HOSTS field under ENVIRONMENT section is missing in conf file",
                                    "red"))
                            sys.exit(1)
                    except KeyboardInterrupt:
                        print('Keyboard Interrupt')
                        sys.exit(1)
                    except (KeyError, ValueError):
                        print(
                            colored(
                                "SSH_HOSTS field under ENVIRONMENT section is missing in conf file",
                                "red"))
                        sys.exit(1)
                    except Exception as e:
                        print(colored("Error in parsing SSH_HOSTS field %s" % e))
                    if key.lower() == 'hosts':
                        conf_data[section]['ips'] = list()
                        conf_data[section]['ports'] = list()
                    else:
                        conf_data[section]['vip_ips'] = list()
                        conf_data[section]['vip_ports'] = list()
                    for data in value.split(','):
                        if not re.match(ip_port_format, data):
                            cmd = section + ">" + key + \
                                "> The ip:port(%s) format is not valid" % data
                            conf_invalid_data.append(cmd)
                            continue
                        else:
                            if not len(data.split(":")) == 2:
                                cmd = section + ">" + key + \
                                    "> The ip:port (%s) format is not valid" % data
                                conf_invalid_data.append(cmd)
                                continue
                        ip, port = data.split(colon)
                        if ip not in conf_data['ENVIRONMENT']['ips']:
                            cmd = section + ">" + key + \
                                "> The ip (%s) is not present in SSH_HOST field" % ip
                            conf_invalid_data.append(cmd)
                            continue
                        if not port_checker(port):
                            cmd = section + ">" + key + \
                                "> The port (%s) value is not valid(It should be between 0 and 65535)" % port
                            conf_invalid_data.append(cmd)
                            continue
                        conf_data[section][key.lower()] = list()
                        conf_data[section][key.lower()] = value.split(',')
                        port_check.append(data)
                        if key.lower() == 'hosts':
                            conf_data[section]['ips'].append(data.split(colon)[0])
                            conf_data[section]['ports'].append(
                                data.split(colon)[1])
                        else:
                            conf_data[section]['vip_ips'].append(
                                data.split(colon)[0])
                            conf_data[section]['vip_ports'].append(
                                data.split(colon)[1])

        table = PrettyTable([Bcolors.FAIL + "SECTION" + Bcolors.ENDC,
                             Bcolors.FAIL + "FIELD" + Bcolors.ENDC,
                             Bcolors.FAIL + "Error in conf file" + Bcolors.ENDC])
        if len(conf_invalid_data):
            for result in conf_invalid_data:
                table.hrules = True
                section_data, field_data, error_data = result.split('>')
                table.add_row(
                    [str(section_data),
                     str(field_data),
                     str(error_data)])
            print(table)
            sys.exit(1)
        port_duplicate = set([x for x in port_check if port_check.count(x) > 1])
        if len(port_duplicate):
            print(colored("The following ports are duplicate in conf file", "red"))
            print(port_duplicate)
            sys.exit(1)
        pickle_file = current_path + '/conf_data.p'
        hash_file = current_path + '/.conf_hash.txt'
        
        with open(hash_file,'w') as conf_hash,open(conf_file,'r') as conf,open(pickle_file,'wb') as pickle_object:
            pickle.dump(conf_data,pickle_object)
            conf_hash.write(hashlib.md5(conf.read().encode('utf-8')).hexdigest())

    else:
        conf_object = open(current_path + '/conf_data.p','rb')
        conf_data = pickle.load(conf_object)
        conf_object.close()

    nodes = []
    for d in conf_data['ENVIRONMENT']['datacenter']:
        d = d.split(':')[1]
        n = d.split(',')
        for m in n:
            nodes.append(m)
    nodes.sort()
    to_check_nodes = conf_data['ENVIRONMENT']['ips']
    to_check_nodes.sort()
    d = (nodes > to_check_nodes) - (nodes < to_check_nodes)

    if not d == 0:
        print(colored('All the ips are not configured in the datacenter field in the conf file.', 'red'))
        sys.exit(1)
    to_exit = False

    for plug in conf_data['PLUGINS']['plugins']:
        try:
            conf_data['PLUGINS'][plug]['ips']
            conf_data['PLUGINS'][plug]['ips']
        except KeyError:
            print('<IP>:<PORT> details are not found for: ' + plug)
            to_exit = True

    if to_exit:
        sys.exit(1)
    return conf_data