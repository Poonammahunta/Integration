"""HTTP-HTTPS converiosn."""
# The script is used to convert appviewx components
# from HTTP to HTTPS and vice-versa.
# Usage:
#         ./appviewx --enable-https <component>
#         ./appviewx --disable-https <component>

import os
import sys
import web
import time
import signal
import socket
import logger
import plugin
import gateway
import subprocess
from termcolor import colored
from config_parser import config_parser
from mongodb_setup import print_success
from initialize_web import InitializeWeb
from avx_commons import sigint_handler
from initialize_common import InitializeCommon
from initialize_plugins import InitializePlugins
from initialize_gateway import InitializeGateway

import avx_commons
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
signal.signal(signal.SIGINT, sigint_handler)
hostname = socket.gethostbyname(socket.gethostname())
current_file_path = os.path.dirname(os.path.realpath(__file__))
lggr = logger.avx_logger('http-https')


def help_fun():
    """Function to displat usage of http-https conversion."""
    print('Help function for HTTP-HTTPS conversion')
    print('Options:')
    print('\t1. --enable-https')
    print('\t2. --disable-https')
    print('Usage:')
    print('\t./appviewx --enable-https all/plugins/gateway/web')
    print('\t./appviewx --disable-https all/plugins/gateway/web')
    sys.exit(1)


class Convert():
    """The class to convert components from http to https and vice-versa."""

    def __init__(self, component, state):
        """Declare class variables."""
        self.conf_file = current_file_path + '/../../conf/appviewx.conf'
        self.conf_data = config_parser(self.conf_file)
        self.component = component
        self.state = state
        self.path = self.conf_data['ENVIRONMENT']['path'][
            self.conf_data['ENVIRONMENT']['ips'].index(hostname)]
        if self.state.upper() not in ['HTTP', 'HTTPS']:
            lggr.error('Invalid input given for conversion')
            lggr.debug('The target should be either HTTP or HTTPS.')
            sys.exit(1)
        if self.component.lower() not in ['all', 'plugins', 'gateway', 'web']:
            lggr.error('Not a valid component: ' + component)
            lggr.debug('Not a valid component: ' + component)
            help_fun()
            sys.exit(1)
        lggr.debug('State: ' + self.state)
        lggr.info('State: ' + self.state)

        if self.state.upper() == 'HTTP':
            self.state = 'False'
        else:
            self.state = 'True'

        if self.component == 'all':
            self.component = ['plugins', 'gateway', 'web']
        else:
            self.component = [self.component.lower()]
        lggr.debug('Components to convert: ' + ','.join(self.component))
        lggr.info('Components to convert: ' + ','.join(self.component))

    def edit_in_conf_file(self):
        """Edit the contents of the conf file before conversion."""
        try:
            replacements = {}
            if 'gateway' in self.component:
                replacements['APPVIEWX_GATEWAY_HTTPS'] = self.state
            if 'web' in self.component:
                replacements['APPVIEWX_WEB_HTTPS'] = self.state
            if 'plugins' in self.component:
                replacements['VM_HTTPS'] = self.state
                replacements['ENABLE_CLIENT_CERT'] = self.state
            with open(self.conf_file) as conf_file:
                conf_content = conf_file.readlines()
            out_content = []
            for line in conf_content:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=')
                    for dic_key, dic_value in replacements.items():
                        if key.strip() == dic_key:
                            line = dic_key + '=' + dic_value + '\n'
                            lggr.debug('New line added in conf file: ' + line)
                out_content.append(line)
            with open(self.conf_file, 'w+') as conf_file:
                lggr.debug('Writing new values to conf_file')
                conf_file.writelines(out_content)
        except Exception as e:
            print(e)
            lggr.error(e)

    def initialize_components(self):
        """Function to initialize components for converting."""
        try:
            lggr.debug('Initializing common components')
            InitializeCommon.initialize(InitializeCommon())
            print_success('Common Components', 'Initialized')
            if 'plugins' in self.component:
                lggr.debug('Initializing Plugins')
                print_success('Plugins', 'Initialized')
                InitializePlugins.initialize(InitializePlugins())
            if 'gateway' in self.component:
                lggr.debug('Initializing Gateway')
                print_success('Gateway', 'Initialized')
                InitializeGateway.initialize(InitializeGateway())
            if 'web' in self.component:
                lggr.debug('Initializing Web')
                print_success('Web', 'Initialized')
                InitializeWeb.initialize(InitializeWeb())
        except Exception as e:
            print(e)
            lggr.error(e)

    def restart_components(self):
        """Method to restart the components."""
        try:
            if 'plugins' in self.component:
                params = ['--restart', 'plugins']
                plugin_ob = plugin.Plugin(params, self.conf_data)
                lggr.debug('Restarting plugins')
                plugin_ob.operation()
            t_time = time.time() + 60 * 2
            print (colored(
                "Waiting for avx-common to be started" +
                "(It may take upto 2 mins)",
                "cyan"))
            while time.time() < t_time:
                cmd = 'cd ' + self.path + '/scripts && ./appviewx' + \
                    ' --status plugins avx-common'
                ps = subprocess.run(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if 'not running' not in ps.stdout.decode().lower():
                    break
            params = ['--restart', 'gateway']
            gateway_ob = gateway.Gateway(params, self.conf_data)
            lggr.debug('Restarting Gateway')
            gateway_ob.operation()
            if 'web' in self.component:
                params = ['--stop', 'web']
                lggr.debug('Restarting Web')
                web_ob = web.Web(params, self.conf_data)
                web_ob.operation()
                params = ['--start', 'web']
                web_ob = web.Web(params, self.conf_data)
                web_ob.operation()

        except Exception as e:
            print(e)
            lggr.error(e)

    def operation(self):
        """Method to perform th conversion operation."""
        try:
            self.edit_in_conf_file()
            from conf_sync import ConfSync
            ob = ConfSync()
            self.initialize_components()
            self.restart_components()
            ob.initialize()
        except Exception as e:
            print(e)
            lggr.error(e)

if __name__ == '__main__':
    user_input = sys.argv
    component = user_input[1]
    state = user_input[2]
    ob = Convert(component, state)
    ob.operation()
