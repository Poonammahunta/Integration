"""."""
import os
from configobj import ConfigObj
import logger
from status import status as comp_stat
from config_parser import config_parser
location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../conf"))
config = ConfigObj(location + '/appviewx.conf')
# conf_data = config_parser(location + '/appviewx.conf')
lggr = logger.avx_logger('update_conf')


class UpdateConf():
    """The class to create the monitor.conf."""

    def __init__(self, fresh=False, on=True):
        """."""
        conf_file = location + '/appviewx.conf'
        self.conf_data = config_parser(conf_file)
        self.component_list = []
        self.fresh = fresh
        if self.fresh:
            self.status = 'on'
        else:
            self.status = 'off'
        self.on = on

    def db_details(self):
        """."""
        self.component_list.append('[MONGODB]' + '\n')
        for ip, port in zip(self.conf_data['MONGODB']['ips'],
                            self.conf_data['MONGODB']['ports']):
            if self.fresh:
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'db', str(ip), str(port), self.status))
            else:
                status = comp_stat.getStatus(comp_stat(), ['mongodb', ip])
                if status.lower() == 'true':
                    status = 'on'
                else:
                    status = 'off'
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'db', str(ip), str(port), status))
        self.component_list.append('\n')
        self.component_list.append('\n')

    def logstash_details(self):
        """."""
        self.component_list.append('[LOGSTASH]' + '\n')
        for ip, port in zip(self.conf_data['LOGSTASH']['ips'],
                            self.conf_data['LOGSTASH']['ports']):
            if self.fresh:
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'logstash', str(ip), str(port), self.status))
            else:
                status = comp_stat.getStatus(comp_stat(), ['logstash', ip])
                if status.lower() == 'true':
                    status = 'on'
                else:
                    status = 'off'
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'logstash', str(ip), str(port), status))
        self.component_list.append('\n')

    def gateway_details(self):
        """."""
        self.component_list.append('[GATEWAY]' + '\n')
        for ip, port in zip(self.conf_data['GATEWAY']['ips'],
                            self.conf_data['GATEWAY']['ports']):
            if self.fresh:
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'gateway', str(ip), str(port), self.status))
            else:
                status = comp_stat.getStatus(comp_stat(), ['gateway', ip])
                if status.lower() == 'true':
                    status = 'on'
                else:
                    status = 'off'
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'gateway', str(ip), str(port), status))
        self.component_list.append('\n')

    def web_details(self):
        """."""
        self.component_list.append('[WEB]' + '\n')
        for ip, port in zip(self.conf_data['WEB']['ips'],
                            self.conf_data['WEB']['ports']):
            if self.fresh:
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'web', str(ip), str(port), self.status))
            else:
                status = comp_stat.getStatus(comp_stat(), ['web', ip])
                if status.lower() == 'true':
                    status = 'on'
                else:
                    status = 'off'
                self.component_list.append("{0} {1} {2} = {3}\n".format(
                    'web', str(ip), str(port), status))
        self.component_list.append('\n[SCHEDULER]' + '\n')
        self.component_list.append('scheduler = true')
        self.component_list.append('\n')

    def plugin_details(self):
        """."""
        self.component_list.append('[PLUGINS]' + '\n')
        for plugin in self.conf_data['PLUGINS']['plugins']:
            for ip, port in zip(self.conf_data['PLUGINS'][plugin]['ips'],
                                self.conf_data['PLUGINS'][plugin]['ports']):
                if self.fresh:
                    self.component_list.append('{0} {1} {2} = {3}\n'.format(
                        plugin, str(ip), str(port), self.status))
                else:
                    status = comp_stat.getStatus(
                        comp_stat(), ['plugins', plugin, ip, port])
                    if status.lower() == 'true':
                        status = 'on'
                    else:
                        status = 'off'
                    self.component_list.append('{0} {1} {2} = {3}\n'.format(
                        plugin, str(ip), str(port), status))
        self.component_list.append('\n')

    def initialize(self):
        """."""
        self.component_list.append('[CONFIGURATION]' + '\n')
        if self.on:
            self.component_list.append('MONITOR = True' + '\n\n')
            self.db_details()
            self.plugin_details()
            self.gateway_details()
            self.logstash_details()
            self.web_details()
        else:
            self.component_list.append('MONITOR = False' + '\n\n')
        with open(location + '/monitor.conf', 'w+') as mon_conf:
            mon_conf.writelines(self.component_list)
        from monitorconfigure import synchronise
        synchronise()

if __name__ == '__main__':

    ob = UpdateConf()
    ob.initialize()
