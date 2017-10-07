#!../../Python/bin/python
"""File to perform conf_sync across the nodes."""
import os
import socket
import sys
import subprocess
import logger
from fabric.api import *
from fabric import state
from termcolor import colored
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('conf_sync')
fab_ob = None
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
state.output['status'] = False
state.output['stdout'] = False
state.output['running'] = False
state.output['aborts'] = False

def put_file(localpath, remotepath):
    put(localpath, remotepath)

def help_fun():
    """help_fun display text to guide user in case of invalid arguments given by user or upon request."""
    print(colored('\n    usage: ./appviewx --conf-sync \n', 'yellow'))
    return True

class ConfSync():
    """The class to initialize common components."""

    def __init__(self):
        """."""
        from config_parser import config_parser
        self.conf_file = current_file_path + '/../../conf/appviewx.conf'
        self.conf_data = config_parser(self.conf_file)
        self.hostname = socket.gethostbyname(socket.gethostname())
        self.multinode = self.conf_data['ENVIRONMENT']['multinode'][0]
        self.plugin_conf_files = []

    @staticmethod
    def exists_remote(host, path, conn_port):
        """Test if a file exists at path on a host accessible with SSH."""
        cmd = 'ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + ' ' + host + ' [ -d ' + path + ' ] && echo "yes" || echo "no" 2>/dev/null'
        ps = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        status = ps.stdout.decode().strip()
        if status == 'yes':
            lggr.debug(path + ' found at ' + host)
            return True
        if status == 'no':
            lggr.debug(path + ' not found at ' + host)
            return False

    def get_plugin_confs(self, path):
        """."""
        try:
            os.chdir(path)
            for file in os.listdir(path):
                dirname, filename = os.path.split(os.path.abspath(file))
                file = dirname + '/' + filename
                if os.path.isdir(file):
                    self.get_plugin_confs(file)
                    os.chdir('..')
                else:
                    if file.endswith('.conf'):
                        self.plugin_conf_files.append(file)
            lggr.debug('Found the following plugin confs : ' + ','.join(self.plugin_conf_files))
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def plugin_conf(self, node, conn_port):
        """."""
        try:
            plugins_path = current_file_path + '/../../Plugins/'
            self.get_plugin_confs(plugins_path)
            for conf in self.plugin_conf_files:
                usr = node.split(":")[0].split("@")[0]
                f = conf.split('Plugins/')[1]
                remotepath = node.split(":")[1] + "/Plugins/" + f
                remotepath = "/".join(remotepath.split("/")[:-1])
                try:
                    execute(put_file, localpath = conf, remotepath = remotepath, hosts = [node.split(":")[0] + ':' + self.conf_data['ENVIRONMENT']['ssh_port'][0]])
                except:
                    print (node.split(":")[0].split("@")[1] + ": Remote Host Not Reachable")
                    lggr.info(node.split(":")[0].split("@")[1] + ": Remote Host Not Reachable")
                    return 0
            lggr.info('Plugins confs synced to ' + node)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def conf_sync(node, appviewx_conf, bigdata_conf, conn_port):
        """."""
        try:
            from config_parser import config_parser
            conf_data = config_parser(current_file_path + '/../../conf/appviewx.conf')
            cmd_list = []
            cmd = 'rsync  -e \"ssh -q -oStrictHostKeyChecking=no -p ' + conn_port + '\" ' + appviewx_conf + ' ' + bigdata_conf + ' ' + node + '/conf/'
            cmd_list.append(cmd)
            for cmd in cmd_list:
                usr = node.split(":")[0].split("@")[0]
                remotepath =  node.split(":")[1] + "/conf"
                localpath = os.path.realpath(appviewx_conf)
                localpath1 = os.path.realpath(bigdata_conf)
                try:
                    execute(put_file, localpath = localpath, remotepath = remotepath, hosts = [node.split(":")[0]+':' + conf_data['ENVIRONMENT']['ssh_port'][0]])
                    execute(put_file, localpath = localpath1, remotepath = remotepath, hosts = [node.split(":")[0]+':' + conf_data['ENVIRONMENT']['ssh_port'][0]])
                except:
                    print (node.split(":")[0].split("@")[1] + ": Remote Host Not Reachable")
                    lggr.info(node.split(":")[0].split("@")[1] + ": Remote Host Not Reachable")

                    return 0
            lggr.info('appviewx.conf and bigdata.conf synced to ' + node)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def initialize(self):
        """."""
        try:
            if self.multinode.upper() == 'TRUE':
                appviewx_conf = self.conf_file
                bigdata_conf = current_file_path + '/../../conf/bigdata.conf'
                invalid_nodes = {}
                nodes = self.conf_data['ENVIRONMENT']['ssh_hosts']
                nodes = [node for node in nodes if self.hostname not in node]
                for node in nodes:
                    host, path = node.split(':')
                    conn_port = self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(host.split('@')[1])]
                    conn_port = str(conn_port)
                    # status = self.exists_remote(host, path, conn_port)
                    status = True
                    if status is True:
                        self.conf_sync(node, appviewx_conf, bigdata_conf, conn_port)
                        # self.plugin_conf(node, conn_port)
                    else:
                        invalid_nodes[host] = path
                if len(invalid_nodes):
                    for node in invalid_nodes:
                        print(colored(invalid_nodes[node] + ' not found on ' + node, 'red'))
                return 0
            return 4
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

if __name__ == '__main__':
    user_input = sys.argv
    if len(user_input) > 1:
        print('File takes no input!')
        print('Exiting')
        sys.exit(1)

    ob = ConfSync()
    ret_code = ob.initialize()

    if ret_code == 4:
        print('conf-sync works only in case of multinode setup!')
        lggr.info('conf-sync works only in case of multinode setup!')
    else:
        print('Conf-sync completed successfully')
        lggr.info('Conf-sync completed successfully')
