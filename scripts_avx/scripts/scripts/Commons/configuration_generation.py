"""."""
import sys
import getpass
import re
import socket
import os
import getpass
import configparser
import subprocess

import signal
current_user = getpass.getuser()
current_ip = socket.gethostbyname(socket.gethostname())


def key_int(signal, frame):
    """Handle Keyboard Interrupt."""
    sys.exit(1)

signal.signal(signal.SIGINT, key_int)


class conf_file_generation():
    """."""

    def __init__(self):
        """."""
        pass

    def ipv4_validation(self, ip):
            if not re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):
                try:
                    return None
                except KeyboardInterrupt:
                    sys.exit(1)
            return ip

    def port_checker(self, port):
        """To check Whether the port is valid or invalid(It should be int and in range between(0,65535)
            Args:
                (integer)
            Example:
                (5000)
            Return Value:
                True: if it is valid
                False: if it is invalid
        """
        try:
            isinstance(int(port), int)
            if int(port) > 65535 or int(port) < 1024:
                try:
                    port = input("Please enter port in range 1024 and 65535: ")
                except KeyboardInterrupt:
                    sys.exit(1)
                return self.port_checker(port)
            return port
        except ValueError:
            return None

    def number_of_nodes(self):
        """."""
        valid = True
        while valid:
            no_of_nodes = input("Enter number of nodes (1,3,5,7,9 or 11): " )
            if no_of_nodes not in ["1", "3", "5", "7", "11"] or no_of_nodes == "":
                print ("Please specify a number from the above given list.")
            else:
                valid = False

        return int(no_of_nodes)

    def get_ips(self, no_of_nodes):
        """."""
        node_ips = list()
        usernames = list()
        location = list()
        if int(no_of_nodes) == 1:
            node_ips.append(current_ip)
            usernames.append(current_user)
            while True:
                path = input('Enter the AppViewX installation path: ')
                if not os.path.isabs(path):
                    print ("Enter Valid Path")
                    continue
                else:
                    break
            location.append(path)
        else:
            try:
                verified = 0
                total = 0
                node_number = 1
                while node_number <= no_of_nodes:
                    try:
                        ip_user_path = input('Enter the ip details in the format <username@ip'+ str(node_number) + ':location>:  ')
                    except KeyboardInterrupt:
                        sys.exit(1)
                    try:
                        ip = ip_user_path.split('@')[1]
                        ip = ip.split(':')[0]
                        ip = self.ipv4_validation(ip)
                        if not ip == None:
                            username = ip_user_path.split('@')[0]
                            usernames.append(username)
                            path = ip_user_path.split(':')[1]
                            if ip in node_ips:
                                print ("IP Already Exists")
                                continue
                            node_ips.append(ip)
                            location.append(path)
                            total = total + 1
                            node_number = node_number + 1
                        else:
                            print ('INVALID format.Please enter again')
                    except Exception as e:
                        print ("INVALID format.Please enter again")
                        continue

                if current_ip not in node_ips:
                    print ('Ip ' + current_ip + ' is missing in ip details')
                    sys.exit(1)
            except Exception as e:
                print ("Error in giving the ip details please do run the program again")
        return node_ips,usernames,location

    def get_port_confirmation(self, node_ips):
        """."""
        ip_port_information = list()
        for ip in node_ips:
            try:
                port_range = input('Port range for AppViewX components in  ' + ip +  ' (Default: 5000-6000):')
                if port_range == '':
                    lower_port_level = '5000'
                    upper_port_level = '6000'
                else:
                    lower_port_level = port_range.split('-')[0].strip()
                    upper_port_level = port_range.split('-')[1].strip()
            except KeyboardInterrupt:
                sys.exit(1)
            try:
                lower_port_level =  self.port_checker(lower_port_level)
                lower_port_level = int(lower_port_level)
            except Exception as e:
                print (e)
                sys.exit(1)
            try:
                if int(upper_port_level) > int(lower_port_level):
                    upper_port_level = self.port_checker(upper_port_level)
                else:
                    print ("Upper Port Level should be greater than Lower Port Level.")
                    return self.get_port_confirmation(node_ips)
            except Exception as e:
                print (e)
                sys.exit(1)
            ip_port_information.append((ip, lower_port_level, upper_port_level))
        return ip_port_information

    def iagent_section(self, nodes, ports, conf_object):
        """."""
        if len(nodes) == 1:
            multinode = 'FALSE'
        else:

            multinode = 'TRUE'
        hosts = str()
        if len(nodes) == 1:
            hosts = 'localhost:' + str(ports[0] + 3) + ':agent_1'
        else:
            agent_no = 1
            for i in range(len(nodes) - 1):
                if i == 0:
                    hosts = nodes[i] + ":" + str(ports[i] + 3) + ':agent_' + str(agent_no)
                    agent_no = agent_no + 1
                    hosts = hosts + ',' + nodes[i] + ':' + str(ports[i] + 4) + ':agent_' + str(agent_no)
                    agent_no = agent_no + 1
                else:
                    hosts = hosts + ',' + nodes[i] + ":" + str(ports[i] + 3 ) + ':agent_' + str(agent_no)
                    agent_no = agent_no + 1
                    hosts = hosts + ',' + nodes[i] + ':' + str(ports[i] + 4) + ':agent_' + str(agent_no)
                    agent_no = agent_no + 1
        conf_object.set('IAGENT','MULTINODE',multinode)
        conf_object.set('IAGENT','HOSTS',hosts)
        iagent_section_details = "[IAGENT]\nMUTLINODE=" + multinode + '\nHOSTS=' + hosts + '\n' + "LOG_PLUS_ACCESS = FALSE \nLOG_PLUS_IAGENT_VIP=\nLOG_PLUS_IAGENT_PORT=\nLOG_LEVEL=INFO\n"
        return conf_object

    def service_section(self, nodes, ports,conf_object):
        """."""
        if len(nodes) == 1:
            multinode = 'FALSE'
        else:
            multinode = 'TRUE'
        hosts = str()
        if len(nodes) == 1:
            hosts = 'localhost:' + str(ports[0] + 1)
        else:
            for i in range(0, len(nodes)-1):
                if i == 0:
                    hosts = nodes[i] + ":" + str(ports[i] + 1)
                else:
                    hosts = hosts + ',' + nodes[i] + ":" + str(ports[i] + 1)
        conf_object.set('SERVICE','MULTINODE',multinode)
        conf_object.set('SERVICE','HOSTS',hosts)
        # service_section_details = "[SERVICE]\nMUTLINODE=" + multinode + '\nHOSTS=' + hosts + '\n' + "LOG_PLUS_ACCESS = FALSE \nLOG_PLUS_SERVICE_VIP=\nLOG_PLUS_SERVICE_PORT=\nLOG_LEVEL=INFO\n"
        return conf_object

    def web_section(self, nodes, ports,conf_object):
        """."""
        if len(nodes) == 1:
            multinode = 'FALSE'
        else:
            multinode = 'TRUE'
        hosts = str()
        if len(nodes) == 1:
            hosts = 'localhost:' + str(ports[0] + 5)
        else:
            for i in range(0, len(nodes)-1):
                if i == 0:
                    hosts = nodes[i] + ":" + str(ports[i] + 5)
                else:
                    hosts = hosts + ',' + nodes[i] + ":" + str(ports[i] + 5)
        conf_object.set('WEB','MULTINODE',multinode)
        conf_object.set('WEB','HOSTS',hosts)
        return conf_object

    def mongo_section(self, nodes, ports,conf_object):
        """."""
        if len(nodes) == 1:
            multinode = 'FALSE'
        else:
            multinode = 'TRUE'
        hosts = str()
        if len(nodes) == 1:
            hosts = 'localhost:' + str(ports[0])
        else:
            for i in range(3):
                if i == 0:
                    hosts = nodes[i] + ":" + str(ports[i])
                else:
                    hosts = hosts + ',' + nodes[i] + ":" + str(ports[i])
        conf_object.set('MONGODB','MULTINODE',multinode)
        conf_object.set('MONGODB','HOSTS',hosts)
        return conf_object

    def gateway_section(self, nodes, ports,conf_object):
        """."""
        if len(nodes) == 1:
            multinode = 'FALSE'
        else:
            multinode = 'TRUE'
        hosts = str()
        if len(nodes) == 1:
            hosts = 'localhost:' + str(ports[0] + 6)
        else:
            for i in range(0, len(nodes)-1):
                if i == 0:
                    hosts = nodes[i] + ":" + str(ports[i] + 6)
                else:
                    hosts = hosts + ',' + nodes[i] + ":" + str(ports[i] + 6)
        conf_object.set('GATEWAY','MULTINODE',multinode)
        conf_object.set('GATEWAY','HOSTS',hosts)
        return conf_object

    def get_usernames(self, nodes):
        """."""
        usernames = list()
        if len(nodes) == 1:
            usernames.append(current_user)
        else:
            for node in nodes:
                try:
                    usernames.append(input("Enter the username for the " + node + ':\n'))
                except KeyboardInterrupt:
                    sys.exit(1)

        return usernames

    def get_plugins(self,nodes,conf_object,ports):
        total_nodes = len(nodes)
        plugins = os.listdir('Plugins')
        subsystem = str()
        for i in range(len(plugins)):
                dir_files = os.listdir('Plugins/' + plugins[i])
                for file in dir_files:
                    if file.endswith('.jar'):
                        file = file.split('.')[0]
            
                        if i == 0:
                            subsystem = plugins[i]
                        else:
                            subsystem = subsystem + ',' + plugins[i]
        conf_object.set('PLUGINS','ENABLED_PLUGINS',subsystem)

    def get_password(self, nodes, usernames):
        """."""
        password = list()
        if len(nodes) == 1:
            password = []
        else:
            for i in range(len(nodes)):
                password.append(getpass.getpass("Enter the password for " + usernames[i] + '@' + nodes[i] + ':\n'))
        return password

    def get_location(self, nodes):
        """."""
        location = list()
        for node in nodes:
            try:
                location.append(input("Location where the AppViewX to be installed in " + node + ': '))
            except KeyboardInterrupt:
                sys.exit(1)
        return location
    def get_ssh_port(self,conf_object,node_ips):
        if len(node_ips) > 1:
            valid = True
            while valid:
                ssh_port = input('SSH port for internal communication (Default:22):  ')
                if ssh_port == '':
                    ssh_port = str(22)
                if int(ssh_port) < 65535 and int(ssh_port) > 0:
                    conf_object.set('ENVIRONMENT','SSH_PORT',ssh_port)
                    valid = False
                else:
                    print('The port is invalid.')
        return conf_object
    def environment_section(self, nodes, usernames, location,conf_object):
        """."""
        multinode = str()
        if len(nodes) == 1:
            multinode = "FALSE"
        else:
            multinode = "TRUE"
        ssh_hosts = str()
        for ip in range(len(nodes)):
            if ip == 0:
                ssh_hosts = ssh_hosts + usernames[ip] + "@" + nodes[ip] + ':' + location[ip]
            else:
                ssh_hosts =  ssh_hosts + ','+ usernames[ip] + "@" + nodes[ip] + ':' + location[ip]
        conf_object.set('ENVIRONMENT','MULTINODE',multinode)
        conf_object.set('ENVIRONMENT','SSH_HOSTS',ssh_hosts)
        if len(nodes) == 1:
            datacenter = 'Absecon:' + nodes[0]
            default_datacenter = 'Absecon'
        else:
            datacenter = 'Absecon:' + nodes[0] + ' && virginia:' + ','.join(nodes[1:])
            default_datacenter = 'Absecon'
        conf_object.set('ENVIRONMENT','DATACENTER',datacenter)
        conf_object.set('ENVIRONMENT','DEFAULT_DATACENTER',default_datacenter)
        environment_section_details = "[ENVIRONMENT]\nMULTINODE=" + multinode + "\nSSH_HOSTS= "+ ssh_hosts + "\nSSH_PORT=22\nDEFAULT_DATACENTER = Absecon\nDATACENTER = Absecon:localhost\n"

        return conf_object

    def plugins_section(self,nodes,ports,package_location,config_object):
        """."""
        command =  'tar -xvf ' + package_location + ' Plugins -C .'
        try:
            ps = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output = ps.communicate()
        except Exception as e:
            print (e)
            print ("Error in executing the command.")
        plugins = os.listdir('Plugins')
        # print (plugins)
        enabled_plugins = str()
        vms = list() 
        for i in range(len(plugins)):
            if plugins[i].upper() not in ["FRAMEWORK", 'BUILDINFO']:
                vms.append(plugins[i])
                if i==0:
                    enabled_plugins = plugins[i]
                else:
                    enabled_plugins = enabled_plugins + ',' + plugins[i]
            """"
            if not '.' in  plugins[i]:
                files = os.listdir('Plugins/' + plugins[i])
                for file in files:
                    if file.endswith('.jar'):
                        jar_file = file.split('.')[0]
                        vms.append(jar_file)
                        if i == 0:
                            enabled_plugins = plugins[i]
                        else:
                            enabled_plugins = enabled_plugins + ',' + plugins[i]
            """
        enabled_plugins.strip(',')
        config_object.set('PLUGINS','ENABLED_PLUGINS',enabled_plugins)
        # print (vms)
        if len(nodes) == 1:
            for i in range(len(vms)):
                config_object.set('PLUGINS',vms[i],'localhost:' + str(ports[0] + 11 + i) )
        else:
            l = range(0,len(vms))
            vms_index = [l[x:x+len(nodes)] for x in range(0, len(vms), len(nodes))]
            for i in range(len(vms_index)):
                if len(vms_index[i])  == len(nodes):
                    for node_index in range(len(nodes)):
                        port = str(ports[node_index] + 10 + i )
                        if node_index != len(nodes)-1:
                            config_object.set('PLUGINS',vms[vms_index[i][node_index]],nodes[node_index] + ':' + port + ',' + nodes[node_index+1] + ':' + str(int(port)+ 30 + 1))
                        else:
                            config_object.set('PLUGINS',vms[vms_index[i][node_index]],nodes[node_index] + ':' + str(int(port)+  60 + 1) + ',' + nodes[0] + ':' +  str( int(port) + 90 + 1))
                else:
                    for j in range(len(vms_index[i])):
                        port = str(ports[0] + 120 + i + j )
                        config_object.set('PLUGINS',vms[vms_index[i][j]],nodes[0] + ':' + port+ ',' + nodes[1] + ':' +  str(int(port)+1))
        return config_object

    def get_https_option(self,config_object):
        valid = True
        while valid:
            https_option = input('Do you want to enable HTTPS (Yes/No) ?: ')
            if https_option.lower() in ['yes','y','n','no']:
                valid = False
            else:
                print ('INVALID INPUT')

        if https_option.lower() in ['yes','y','n','no']:
            if https_option.lower() in ['yes','y'] : 
                config_object.set('GATEWAY','APPVIEWX_GATEWAY_HTTPS','TRUE')
                config_object.set('WEB','APPVIEWX_WEB_HTTPS','TRUE')
                config_object.set('VM_CONF','VM_HTTPS','TRUE')
                config_object.set('VM_CONF','ENABLE_CLIENT_CERT','FALSE')
            else:
                config_object.set('GATEWAY','APPVIEWX_GATEWAY_HTTPS','FALSE')
                config_object.set('WEB','APPVIEWX_WEB_HTTPS','FALSE')
                config_object.set('VM_CONF','VM_HTTPS','FALSE')
                config_object.set('VM_CONF','ENABLE_CLIENT_CERT','FALSE')

        return config_object

    def conf_generate_start(self,package_location):
        """."""
        command = 'tar -xvf ' + package_location + ' conf/appviewx.conf -C . ; mv conf/appviewx.conf .'
        try:
            ps = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output = ps.communicate()
        except Exception as e:
            print (e)
            print ("Error in executing the command.")
        config = configparser.SafeConfigParser(allow_no_value=True)
        config.optionxform  =str
        file_obj = open('appviewx.conf')
        config.readfp(file_obj)
        total_nodes = self.number_of_nodes()
        ips,usernames,location = self.get_ips(total_nodes)
        # usernames = self.get_usernames(ips)
        # password = self.get_password(ips, usernames)
        # location = self.get_location(usernames)
        ip_port_details = self.get_port_confirmation(ips)
        lower_ports = list()
        for detail in ip_port_details:
            lower_ports.append(detail[1])
        content = str()
        config = self.environment_section(ips, usernames, location,config)
        config = self.get_ssh_port(config,ips)
        # config = self.iagent_section(ips,lower_ports,config)
        # config = self.service_section(ips,lower_ports,config)
        config = self.gateway_section(ips,lower_ports,config)
        config = self.mongo_section(ips,lower_ports,config)
        config = self.web_section(ips,lower_ports,config)
        config = self.plugins_section(ips,lower_ports,package_location,config)
        config = self.get_https_option(config)
        # Merging Comments with Original Configuration file
       
        with open('appviewx.conf', 'w') as in_file:
            config.write(in_file)
        os.system('rm -rf conf')

if __name__ == "__main__":

    try:
        package_location = sys.argv[1]
        conf_file_generation.conf_generate_start(conf_file_generation(),package_location)
    except KeyboardInterrupt:
        print ("Keyboard Interrupt")
        sys.exit(1)
    except Exception as e:
        print ('Error in generating the conf file')
        sys.exit(1)
