"""Monitoring script for AVX components."""
import configparser
import subprocess
import os
import sys
from time import sleep
from status import status
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
from time import time
import avx_commons
from config_parser import config_parser
import socket
from configobj import ConfigObj
from avx_commons import return_status_message_fabric
from using_fabric import AppviewxShell
from avx_commons import get_username_path
from datetime import datetime
s = status()
location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../conf"))
log_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../logs"))
script_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../"))
hostname = socket.gethostbyname(socket.gethostname())
sys.path.insert(0, script_location + '/Plugins')
sys.path.insert(0, script_location + '/Mongodb')
sys.path.insert(0, script_location + '/Gateway')
sys.path.insert(0, script_location + '/Web')

RotatingFileHandler(log_location + '/avx-watchdog.log', maxBytes=20, backupCount=5)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_location + '/avx-watchdog.log',
                    filemode='a',)


class WatchDog():
    """The watchdog class monitors the components."""

    """In case a component is stopped using the
    appviewx commands, then the component will not be started automatically."""

    def __init__(self):
        """."""
        logging.info('Running the avx-watchdog on: ' + str(datetime.now()))
        self.mon_conf_file = location + '/monitor.conf'
        if os.path.exists(self.mon_conf_file):
            logging.debug('monitor.conf found in the conf directory.')
        else:
            logging.error('monitor.conf not found in the conf directory.')
            logging.debug('monitor.conf not found in the conf directory.')
        self.Config = configparser.ConfigParser()
        app_conf_file = location + '/appviewx.conf'
        self.conf_data = config_parser(app_conf_file)
        self.load_average = float()
        self.percent_mem_usage = float()
        self.payload = {
            "payload": {
                "severity": "Critical",
                "name": "Infrastructure",
                "message": "restart the component",
                "category": "Appviewx",
                "deviceName": "<device-hostname>",
                "deviceId": "<device-ip>",
                "source": "gateway",
                "sourceId": "Infrastructure",
                "time": 1491979028}}

    def check_plug(self):
        """Check status of plugins."""
        gw_reload = False
        self.Config.read(location + "/monitor.conf")
        cmd_for_gateway_status = 'cd ' + script_location + ' ; ' +\
            './appviewx --status gateway'
        ps = subprocess.run(cmd_for_gateway_status, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        res = ps.stdout.decode()
        if 'not running' not in res.lower():
            api_hit = True
        else:
            api_hit = False
        if api_hit:
            property_file = script_location +\
                '/../properties/appviewx.properties'
            prop_data = ConfigObj(property_file)
            gw_url = prop_data['GATEWAY_BASE_URL']
            api_url = gw_url.rstrip('/') + '/avxmgr/vmstatus'
            response, url_response = avx_commons.process_status(api_url, True)
            if response.lower() == 'pageup':
                status_data = url_response.json()
        else:
            status_data = {}
        all_plugins = self.Config.options("PLUGINS")
        for plugs in all_plugins:
            plug1 = self.Config.get('PLUGINS', plugs)
            plug_define = plugs.split(" ")
            container_id = avx_commons.jar_name(plug_define[0], True)
            datacenter = avx_commons.get_datacenter(
                self.conf_data, plug_define[1])
            if api_hit:
                output = status_data[container_id][datacenter][
                    plug_define[1] + ':' + plug_define[2]]
                if output.lower() != 'running':
                    output = 'False'
            else:
                output = avx_commons.port_status(
                    plug_define[1], plug_define[2])
                if output == 'open':
                    output = 'False'
            if plug1 == "on" and output == "False":
                logging.debug('Plugin ' + plug_define[0] + ' on ' +
                              plug_define[1] + ':' + plug_define[2] +
                              ' seems to be killed improperly!')
                cmd = "cd " + script_location +\
                    "; ./appviewx --start plugins {0} {1} {2}".format(
                        plug_define[0], plug_define[1], plug_define[2])
                logging.debug('Attempting to start plugin ' + plug_define[0] +
                              ' on ' + plug_define[1] + ':' + plug_define[2])
                ps = subprocess.run(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                gw_reload = True
                if not ps.returncode:
                    logging.info(
                        'Plugin ' + plug_define[0] + ' started ' +
                        ' on ' + plug_define[1] + ':' + plug_define[2])
                    logging.debug('Sending alert')
                else:
                    logging.error(
                        'Plugin ' + plug_define[0] + ' not started ' +
                        ' on ' + plug_define[1] + ':' + plug_define[2])
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=plug_define[1],
                                    message=plug_define[0] +
                                    ' plugin started on ' + plug_define[1] +
                                    ':' + plug_define[2])

        if gw_reload:
            from plugin import Plugin
            Plugin.gw_reload(Plugin([], self.conf_data))

    def check_gateway(self):
        """Check status of gateway."""
        self.Config.read(location + "/monitor.conf")
        gateways = self.Config.options("GATEWAY")
        for gateway in gateways:
            gateway_status = self.Config.get("GATEWAY", gateway)
            gateway_define = gateway.split(" ")
            gateway_run = s.getStatus(["gateway", gateway_define[1]])
            if gateway_status == "on" and gateway_run == "False":
                logging.debug('The gateway process on ' + gateway_define[1] +
                              ' seems to be killed improperly.')
                logging.debug('Attempting to start gateway on: ' +
                              gateway_define[1])
                cmd_to_check_status = 'cd ' + script_location +\
                    '; ./appviewx --status plugins avx-common'
                end_time = time() + 60
                while time() < end_time:
                    ps = subprocess.run(cmd_to_check_status,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                    if 'not running' not in ps.stdout.decode().lower():
                        break
                import gateway
                gate_ob = gateway.Gateway(
                    ['--start', 'gateway', gateway_define[1]],
                    self.conf_data)
                gate_ob.operation()
                if not ps.returncode:
                    logging.info('Gateway started on: ' + gateway_define[1])
                    logging.debug('Sending alert now.')
                else:
                    logging.error('Gateway not started on: ' +
                                  gateway_define[1])
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=gateway_define[1],
                                    message='Web started on ' +
                                    gateway_define[1])

    def check_web(self):
        """Check status of web."""
        self.Config.read(location + "/monitor.conf")
        webs = self.Config.options("WEB")
        for web in webs:
            web_status = self.Config.get("WEB", web)
            web_define = web.split(" ")
            web_run = s.getStatus(["web", web_define[1]])
            if web_status == "on" and web_run == "False":
                logging.debug('The web process on ' + web_define[1] +
                              ' seems to be killed improperly.')
                cmd = "cd " + script_location +\
                    "; ./appviewx --start web {0}".format(web_define[1])
                logging.debug('Attempting to start web on: ' +
                              web_define[1])
                ps = subprocess.run(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if not ps.returncode:
                    logging.info('Web started on: ' + web_define[1])
                    logging.debug('Sending alert now.')
                else:
                    logging.error('Web not started on: ' + web_define[1])
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=web_define[1],
                                    message='Web started on ' + web_define[1])

    def check_logstash(self):
        """Check status of logstash."""
        self.Config.read(location + "/monitor.conf")
        logstashs = self.Config.options("LOGSTASH")
        for logstash in logstashs:
            logstash_status = self.Config.get("LOGSTASH", logstash)
            logstash_define = logstash.split(" ")
            logstash_run = s.getStatus(["avx_platform_logs", logstash_define[1]])
            if logstash_status == "on" and logstash_run == "False":
                logging.debug('The logstash process on ' + logstash_define[1] +
                              ' seems to be killed improperly.')
                cmd = "cd " + script_location +\
                    "; ./appviewx --start avx_platform_logs {0}".format(logstash_define[1])
                logging.debug('Attempting to start logstash on: ' +
                              logstash_define[1])
                ps = subprocess.run(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if not ps.returncode:
                    logging.info('Web started on: ' + logstash_define[1])
                    logging.debug('Sending alert now.')
                else:
                    logging.error('Web not started on: ' + logstash_define[1])
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=logstash_define[1],
                                    message='Web started on ' + logstash_define[1])

    def check_db(self):
        """Check status of database."""
        self.Config.read(location + "/monitor.conf")
        for db in self.Config.options("MONGODB"):
            db_status = self.Config.get("MONGODB", db)
            db_define = db.split(" ")
            db_run = s.getStatus(["mongodb", db_define[1]])
            if db_status == "on" and db_run == "False":
                logging.debug('The mongodb on ' + db_define[1] +
                              ' seems to be killed improperly.')
                cmd = "cd " + script_location +\
                    "; ./appviewx --start mongodb {0}".format(db_define[1])
                logging.debug('Attempting to start mongodb on: ' +
                              db_define[1])
                ps = subprocess.run(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                if not ps.returncode:
                    logging.info('Mongodb started on: ' + db_define[1])
                    logging.debug('Sending alert now.')
                else:
                    logging.error('Mongodb not started on: ' + db_define[1])
                sleep(5)
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=db_define[1],
                                    message='Mongodb started on ' +
                                    db_define[1])

    def cpu_usage(self):
        """The function to check th CPU usage."""
        cmd_for_load_average = 'uptime'
        for node in self.conf_data['ENVIRONMENT']['ips']:
            logging.debug('Checking CPU usage for: ' + node)
            user, path = get_username_path(self.conf_data, node)
            command = AppviewxShell([node], user=user)
            f_ob = command.run(cmd_for_load_average)
            stat, res = return_status_message_fabric(f_ob)
            if stat:
                out = res.strip()
            else:
                continue
            load_averages = out.split(':')[-1].strip().split(',')
            load_averages = [x.strip() for x in load_averages]
            poll_interval = self.conf_data['COMMONS'][
                'appviewx_cpu_monitor_poll_interval'][0]
            try:
                poll_interval = int(poll_interval)
            except:
                poll_interval = 15
            logging.debug('Polling interval for CPU usage is: ' + str(
                poll_interval))
            if poll_interval == 1:
                self.load_average = float(load_averages[0].strip())
            elif poll_interval == 5:
                self.load_average = float(load_averages[1].strip())
            else:
                self.load_average = float(load_averages[2].strip())
            logging.debug(
                'The load average value based upon the polling time is: ' +
                str(self.load_average))
            notify_value = float(
                self.conf_data['COMMONS']['appviewx_cpu_usage_notify'][0])
            critical_value = float(
                self.conf_data['COMMONS']['appviewx_cpu_usage_critical'][0])
            if self.load_average > critical_value:
                logging.debug(
                    'CPU usage is above the critical value for: ' + node)
                logging.debug('Sending alert now.')
                if self.sess_id:
                    self.send_alert(severity='Critical',
                                    deviceip=node,
                                    message='CPU usage for ' + node +
                                    ' is above the critical value!!')
            elif self.load_average > notify_value:
                logging.debug(
                    'CPU usage is above the optimum value for: ' + node)
                logging.debug('Sending alert now.')
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=node,
                                    message='CPU usage for ' + node +
                                    ' is greater than optimum value!!')

    def mem_usage(self):
        """Function to check memory usage."""
        cmd_for_procinfo = 'cat /proc/meminfo'
        for node in self.conf_data['ENVIRONMENT']['ips']:
            logging.debug('Checking memory usage for ' + node)
            user, path = get_username_path(self.conf_data, node)
            command = AppviewxShell([node], user=user)
            f_ob = command.run(cmd_for_procinfo)
            stat, res = return_status_message_fabric(f_ob)
            if stat:
                mem_content = res.strip().split('\n')
            else:
                logging.error(
                    'Error in getting the memoryusage information for ' + node)
                continue

            total_mem = ''
            used_mem = ''
            for line in mem_content:
                key, value = line.split(':')
                if key.strip().lower() == 'memtotal':
                    total_mem = int(value.split()[0].strip())
                if key.strip().lower() == 'active':
                    used_mem_active = int(value.split()[0].strip())
                if key.strip().lower() == 'inactive':
                    used_mem_inactive = int(value.split()[0].strip())
            try:
                used_mem = used_mem_inactive + used_mem_active
                self.percent_mem_usage = round(
                    (used_mem * 100) / (float(total_mem)), 2)
                logging.info('Percent Memory Usage for ' + node + ': ' + str(
                    self.percent_mem_usage))
            except:
                print('unable to find values in /proc/meminfo')
                logging.error(
                    'Error in getting the memoryusage information for ' +
                    node + ' from /proc/meminfo file')
                return
            notify_value = float(
                self.conf_data['COMMONS']['appviewx_memory_usage_notify'][0])
            critical_value = float(
                self.conf_data['COMMONS']['appviewx_memory_usage_critical'][0])
            if self.percent_mem_usage > critical_value:
                logging.debug(
                    'Memory usage is above the critical value for: ' + node)
                logging.debug('Sending alert now.')
                if self.sess_id:
                    self.send_alert(severity='Critical',
                                    deviceip=node,
                                    message='Memory usage for ' + node +
                                    ' is above the critical value!!')
            elif self.percent_mem_usage > notify_value:
                logging.debug(
                    'Memory usage is above the optimum value for: ' + node)
                logging.debug('Sending notification now.')
                if self.sess_id:
                    self.send_alert(severity='Notification',
                                    deviceip=node,
                                    message='Memory usage for ' + node +
                                    ' is greater than optimum value!!')

    @staticmethod
    def session_id(gwurl, gwkey, gwsource):
        """Method to get the sessio-id."""
        api_url = gwurl.rstrip('/') +\
            '/avxapi/acctmgmt-perform-login?gwkey=' + gwkey + \
            '&gwsource=' + gwsource
        logging.debug('URL for SessionId: ' + api_url)
        headers = {'username': 'sudo',
                   'password': '74ZB1yoc89G243sl',
                   'Content-Type': 'application/json'}
        try:
            response = requests.post(api_url,
                                     headers=headers,
                                     verify=False,
                                     timeout=10)
        except:
            logging.error('SessionId not generated!')
            logging.debug('SessionId not generated!')
            return "\033[91m SessionId not generated \033[0m"
        response = json.loads(response.text)
        try:
            logging.info('SessionId: ' + response["response"]["SessionId"])
            return response["response"]["SessionId"]
        except:
            logging.error('SessionId not generated!')
            logging.debug('SessionId not generated!')
            return "\033[91m SessionId not generated \033[0m"
        # return "6f538d7b-a0da-48dd-8d2a-e88f0aa74004"

    def send_alert(self, severity='Critical',
                   message='Alert', deviceip=hostname):
        """."""
        from configobj import ConfigObj
        prop_file = location + '/../properties/appviewx.properties'
        prop_content = ConfigObj(prop_file)
        gwurl = prop_content['GATEWAY_BASE_URL']
        gwkey = prop_content['GATEWAY_KEY']
        payload = self.payload
        hosts_file = location + '/../properties/hostnames.txt'
        try:
            with open(hosts_file) as hosts:
                hostcontent = json.loads(hosts.read().strip())
            payload['payload']['deviceName'] = hostcontent[deviceip]
        except:
            payload['payload']['deviceName'] = 'Undefined'
        if not self.sess_id or 'not generated' in self.sess_id:
            print('Unable to send alert as unable to generate Session Id')
            logging.error(
                'Unable to send alert as unable to generate Session Id')
            logging.debug(
                'Unable to send alert as unable to generate Session Id')
            return
        payload['payload']['severity'] = severity
        payload['payload']['message'] = message
        payload['payload']['deviceId'] = deviceip
        payload['payload']['time'] = int(str(time()).split('.')[0]) * 1000
        logging.info('Payload sent with alert: ' + json.dumps(payload))
        alert_url = gwurl.rstrip('/') +\
            '/avxapi/acctmgmt-receive-alert?gwkey=' + gwkey +\
            '&gwsource=WEB'
        logging.debug('hitting the URL: ' + alert_url)
        headers = {
            'SessionId': self.sess_id,
            'Content-Type': 'application/json'}
        p = requests.post(alert_url,
                          headers=headers,
                          data=json.dumps(payload),
                          verify=False, timeout=10)
        if (json.loads(p.text))['response']:
            logging.error('Unable to send alert.')
        else:
            logging.debug('Alert sent.')

    def try_generate_sess_id(self):
        """Functio to genearte session_id at the start of a session."""
        from configobj import ConfigObj
        prop_file = location + '/../properties/appviewx.properties'
        prop_content = ConfigObj(prop_file)
        gwurl = prop_content['GATEWAY_BASE_URL']
        gwkey = prop_content['GATEWAY_KEY']
        gwsource = prop_content['SOURCE']
        for tries in range(5):
            self.sess_id = self.session_id(gwurl, gwkey, gwsource)
            if 'not generated' not in self.sess_id.lower():
                break
            self.sess_id = None
        logging.error(
            'Not able o generate session id for this particular session.')


if __name__ == "__main__":
    while True:
        Config = configparser.ConfigParser()
        Config.read(location + "/monitor.conf")
        Dbs = Config.get("CONFIGURATION", "MONITOR")
        if Dbs.lower() == 'true':
            ob = WatchDog()
            ob.try_generate_sess_id()
            ob.cpu_usage()
            ob.mem_usage()
            ob.check_db()
            ob.check_logstash()
            #ob.check_plug()
            ob.check_web()
            ob.check_gateway()
            logging.debug('#' * 80)
            logging.debug('The process is sleeping for 2 minutes.')
            logging.debug('monitoring cycle over.')
            logging.debug('#' * 80)
            del ob
        print('sleeping')
        sleep(120)
