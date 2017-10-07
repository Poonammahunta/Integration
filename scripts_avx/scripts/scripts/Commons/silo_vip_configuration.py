"""."""
import os
import sys
import socket
import signal
import logging
import avx_commons
from time import sleep
from avx_commons import port_status
from config_parser import config_parser
hostname = socket.gethostbyname(socket.gethostname())
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_path = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('Installer')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(current_file_path + '/../../logs/silo_vip_config.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d}' +
    ' %(levelname)s\t%(message)s',
    '%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


class SiloVIPDeployement():
    """The class to configure ApViewX for silo deployement."""

    """Since AppViewX will be running on silo deployement, the script will monitor
    the gateway and web components of a particular node. If any is down,
    then the load balancer will be advised not to route the traffic to the
    particular node. In case there is no gateway component on a particular
    node, only the we will be monitred."""

    def __init__(self):
        """Define the class variables."""
        conf_file = current_file_path + '/../../conf/appviewx.conf'
        self.conf_data = config_parser(conf_file)
        self.gateway_ips = self.conf_data['GATEWAY']['ips']
        self.gateway_ports = self.conf_data['GATEWAY']['ports']
        self.web_ips = self.conf_data['WEB']['ips']
        self.web_ports = self.conf_data['WEB']['ports']
        self.gateway_status = True
        self.web_status = True

    def gateway_status_check(self):
        """Check the status of gateway for the present node."""
        gateway_ip = hostname
        gateway_port = self.gateway_ports[self.gateway_ips.index(gateway_ip)]
        status = port_status(gateway_ip, gateway_port)
        if not status == 'listening':
            logger.debug('Gateway is not running on: ' + gateway_ip)
            self.gateway_status = False
        else:
            logger.debug('Gateway is running on: ' + gateway_ip)

    def web_status_check(self):
        """Check the status of web for the present node."""
        web_ip = hostname
        web_port = self.web_ports[self.web_ips.index(web_ip)]
        status = port_status(web_ip, web_port)
        if not status == 'listening':
            logger.debug('Web is not running on: ' + web_ip)
            self.web_status = False
        else:
            logger.debug('Web is running on: ' + web_ip)

    def initialize(self):
        """The function to check status of gateway and web."""
        if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'false':
            logger.info(
                'Silo VIP coniguration not required for singlenode setup')
            sys.exit(1)
        if hostname not in self.web_ips:
            logger.info('Since web is not running on current node, exiting!')
            sys.exit(1)
        else:
            self.web_status_check()
        if hostname in self.gateway_ips:
            self.gateway_status_check()
        else:
            logger.debug('No gateway for: ' + hostname)
        status_to_write = str(['down', 'up'][
            self.gateway_status * self.web_status])
        logger.info('Status for VIP routing: ' + status_to_write)
        from avx_commons import get_username_path
        user, path = get_username_path(self.conf_data, hostname)
        with open(path +
                  '/web/apache-tomcat-web/webapps' +
                  '/AppViewXNGWeb/VIPRoutingStatus', 'w+') as stat_file:
            stat_file.write(status_to_write)
            logger.debug('status written to ' + path +
                         '/web/apache-tomcat-web/webapps/AppViewXNGWeb/' +
                         'VIPRoutingStatus')


if __name__ == '__main__':
    while True:
        ob = SiloVIPDeployement()
        ob.initialize()
        try:
            sleep_interval = int(
                ob.conf_data['COMMONS']['monitoring_inerval_for_vip'][0])
        except:
            sleep_interval = 60
        logger.debug('#' * 80)
        logger.debug(
            'The process is sleeping for ' + str(sleep_interval) + ' seconds')
        logger.debug('#' * 80)
        sleep(sleep_interval)
