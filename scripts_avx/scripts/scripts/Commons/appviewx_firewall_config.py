"""."""
import os
import socket
import sys
import glob
import signal
import readline
import subprocess
from time import sleep
import avx_commons
current_file_path = os.path.dirname(os.path.realpath(__file__))
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

def complete(text, state):
    """."""
    return (glob.glob(text + '*') + [None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


def execute_cmd(cmd):
    """The function to execute command."""
    ps = subprocess.run(cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    return ps


class Ports:
    """."""

    def __init__(self, conf_file, port_details):
        """."""
        try:
            self.conf_file = conf_file
            self.port_details = port_details
            self.ports = []
            self.hostname = socket.gethostbyname(socket.gethostname())

        except Exception as e:
            print(e)
            sys.exit(1)

    def get_ports_from_conf_to_port_details(self):
        """."""
        try:
            infile = open(self.conf_file)
            infile_content = infile.readlines()
            infile.close()
            for line in infile_content:
                if line.startswith('HOSTS'):
                    values = line.split('=')[1].strip()
                    nodes = values.split(',')
                    for node in nodes:
                        ip, port = node.split(':')[:2]
                        if ip.strip() == self.hostname or ip == 'localhost':
                            self.ports.append(port.strip())
            self.ports = list(set(self.ports))
            outfile = open(self.port_details, 'a')
            for port in self.ports:
                text_to_append = '\n' + port + '        TCP         YES         YES         eth0'
                outfile.write(text_to_append)
            outfile.close()
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def get_port_details_from_port_details_file(line):
        """."""
        try:
            try:
                int(line.split()[0])
                return line.split()
            except:
                return None
        except Exception as e:
            print(e)
            sys.exit(1)


class FirewallD:
    """."""

    def __init__(self, obj, port_details):
        """."""
        try:
            self.obj = obj
            self.port_details = port_details
            self.state = str()
        except Exception as e:
            print(e)
            sys.exit(1)

    def start_firewalld(self):
        """."""
        try:
            cmd_to_check_state = 'firewall-cmd --state'
            self.state = os.popen(cmd_to_check_state).read().strip()
            cmds_to_start_firewalld = ['systemctl start firewalld',
                                       'systemctl enable firewalld']
            try:
                for command in cmds_to_start_firewalld:
                    execute_cmd(command)
                    sleep(1)
            except:
                print('Error in starting firewalld')
                print('exiting')
                sys.exit(1)

            sleep(2)

            cmd_to_reload = 'firewall-cmd --reload'

            sleep(2)
            try:
                execute_cmd(cmd_to_reload)
            except:
                print('Unable to reload firewalld')

            print('firewalld started')
        except Exception as e:
                print(e)
                sys.exit(1)

    @staticmethod
    def stop_all_services():
        """."""
        try:
            cmds_to_stop_services = ['firewall-cmd --direct --add-rule ipv4 filter OUTPUT 2 -j DROP',
                                     'firewall-cmd --direct --add-rule ipv4 filter INPUT 2 -j DROP']
            try:
                for command in cmds_to_stop_services:
                    execute_cmd(command)
            except Exception as e:
                print(e)
                sys.exit(1)
            print('All ports stopped.')
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def stop_firewalld():
        """."""
        try:
            cmd = 'systemctl stop firewalld'
            execute_cmd(cmd)
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def start_icmp():
        """."""
        try:
            cmd = 'firewall-cmd --add-icmp-block=echo-reply'
            execute_cmd(cmd)
        except Exception as e:
            print(e)
            sys.exit(1)

    def configure(self):
        """."""
        try:
            self.start_firewalld()
            self.stop_all_services()
            infile = open(self.port_details)
            infile_content = infile.readlines()
            infile.close()
            infile_content = list(filter(lambda line: line != '\n', infile_content))
            cmds_to_execute = []
            for line in infile_content:
                if line.startswith('#'):
                    continue
                details = self.obj.get_port_details_from_port_details_file(line)
                if details is not None:
                    port = details[0]
                    tcp = details[1]
                    inbound = details[2]
                    outbound = details[3]

                    if inbound.strip().upper() == 'YES':
                        cmd = 'firewall-cmd --direct --add-rule ipv4 filter '\
                            + 'INPUT 0 -p ' + tcp.strip().lower()  \
                            + ' --dport ' + port.strip() + ' -j ACCEPT'
                        cmds_to_execute.append(cmd)
                    if outbound.strip().upper() == 'YES':
                        cmd = 'firewall-cmd --direct --add-rule ipv4 filter '\
                            + 'OUTPUT 0 -p ' + tcp.strip().lower()  \
                            + ' --sport ' + port.strip() + ' -j ACCEPT'
                        cmds_to_execute.append(cmd)
            for cmd in cmds_to_execute:
                try:
                    execute_cmd(cmd)
                except:
                    pass

            if 'not running' in self.state:
                self.stop_firewalld()
        except Exception as e:
            print(e)
            sys.exit(1)


class IPTables:
    """."""

    def __init__(self, obj, port_details):
        """."""
        try:
            self.IPT = '/sbin/iptables'
            self.obj = obj
            self.port_details = port_details
        except Exception as e:
            print(e)
            sys.exit(1)

    def start_iptables(self):
        """."""
        try:
            list_of_commands = [self.IPT + ' -F',
                                self.IPT + ' -X',
                                self.IPT + ' -t nat -F',
                                self.IPT + ' -t nat -X',
                                self.IPT + ' -t mangle -F',
                                self.IPT + ' -t mangle -X']

            for command in list_of_commands:
                try:
                    execute_cmd(command)
                except:
                    print('Error in executing %s' % command)
                    print('exiting')
                    sys.exit(1)

            sleep(2)
            print('iptables started')
        except Exception as e:
                print(e)
                sys.exit(1)

    def stop_all_ports(self):
        """."""
        try:
            cmd_to_stop_ports = [self.IPT + ' -P INPUT DROP']
            try:
                for command in cmd_to_stop_ports:
                    execute_cmd(command)
            except Exception as e:
                print(e)
                sys.exit(1)
            sleep(2)
            print('All ports stopped.')
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def start_icmp():
        """."""
        try:
            hostname = socket.gethostbyname(socket.gethostname())
            cmds = ['iptables -A INPUT -p icmp --icmp-type 8 -s 0/0 -d ' + hostname +' -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT',
                    'iptables -A OUTPUT -p icmp --icmp-type 0 -s ' + hostname + ' -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT']

            for command in cmds:
                execute_cmd(command)
        except Exception as e:
            print(e)
            sys.exit(1)

    def configure(self):
        """."""
        try:
            self.start_iptables()
            self.stop_all_ports()
            self.start_icmp()
            infile = open(self.port_details)
            infile_content = infile.readlines()
            infile.close()
            infile_content = list(filter(lambda line: line != '\n', infile_content))
            cmds_to_execute = []
            for line in infile_content:
                if line.startswith('#'):
                    continue
                details = self.obj.get_port_details_from_port_details_file(line)
                if details is not None:
                    port = details[0]
                    tcp = details[1]
                    inbound = details[2]
                    outbound = details[3]
                    interface = details[4]

                    if inbound.strip().upper() == 'YES':
                        cmd = 'iptables -A INPUT -p ' + tcp.strip().lower() \
                            + ' --dport ' + port.strip() + ' -i ' \
                            + interface.strip() + ' -j ACCEPT'
                        cmds_to_execute.append(cmd)
                    if outbound.strip().upper() == 'YES':
                        cmd = 'iptables -A OUTPUT -p ' + tcp.strip().lower() \
                            + ' --sport ' + port.strip() + ' -o ' \
                            + interface.strip() + ' -j ACCEPT'
                        cmds_to_execute.append(cmd)
            for cmd in cmds_to_execute:
                try:
                    execute_cmd(cmd)
                except:
                    pass
        except Exception as e:
            print(e)
            sys.exit(1)


if __name__ == '__main__':
    try:
        try:
            uid = int(os.getuid())
            if not uid == 0:
                print('Need root user to run this script!')
                print('exiting!')
                sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

        path = input('Enter path to AppViewX: ')
        port_details = input('Enter path to port_details file: ').strip()

        conf_file = path + '/conf/appviewx.conf'
        obj = Ports(conf_file, port_details)
        obj.get_ports_from_conf_to_port_details()

        cmd_to_check_iptables = 'rpm -q iptables'
        cmd_to_check_firewalld = 'rpm -q firewalld'

        try:
            if 'not installed' in os.popen(cmd_to_check_iptables).read():
                iptables = 'False'
            else:
                iptables = 'True'
        except Exception as e:
            print(e)
            sys.exit(1)

        try:
            if 'not installed' in os.popen(cmd_to_check_firewalld).read():
                firewalld = 'False'
            else:
                firewalld = 'True'
        except Exception as e:
            print(e)
            sys.exit(1)

        option = str()

        if firewalld == 'False':
            if iptables == 'False':
                option = 'None'
                print('Could not find either iptables or firewalld.')
                print('exiting!')
                sys.exit(1)
            else:
                option = 'iptables'
        else:
            print('Choose method of configuring:')
            print('1. iptables')
            print('2. firewalld')
            choice = input('(1 or 2) : ')
            if int(choice) == 1 or choice.lower() == 'iptables':
                option = 'iptables'
            elif int(choice) == 2 or choice.lower() == 'firewalld':
                option = 'firewalld'
            else:
                print('invalid choice')
                print('exiting!')
                sys.exit(1)

        if option == 'iptables':
            ob = IPTables(obj, port_details)
        else:
            ob = FirewallD(obj, port_details)

        ob.configure()

    except Exception as e:
        print(e)
        sys.exit(1)
