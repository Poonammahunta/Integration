"""."""
import os
import sys
import socket
import logger
import using_fabric
import set_path
from time import sleep
from configobj import ConfigObj
import avx_commons
import signal
import configparser
from config_parser import config_parser
import shutil
from avx_commons import get_username_path
from avx_commons import check_accessibility
avx_path = set_path.AVXComponentPathSetting()
lggr = logger.avx_logger('Scheduler_Monitor')
where_am_i = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, where_am_i + '/../Gateway')
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class SchedulerMonitor():
    """Class to monitor Scheduler Jar."""

    """If more than one one instance of the jar is found to be running,
    then extra processes are killed.
    If no instance is found to be running, then the process is started
    on the primary node as specified in the conf file.
    If the primary node is unreachable, then the jar is started
    on any other node."""

    def __init__(self):
        """."""
        conf_file = where_am_i + '/../../conf/appviewx.conf'
        self.conf_data = config_parser(conf_file)
        self.hostname = socket.gethostbyname(socket.gethostname())
        self.mongo_exit = False
        monitor_conf = os.path.abspath(
            where_am_i + '/../../conf/monitor.conf')
        self.config = configparser.ConfigParser()
        self.config.read(monitor_conf)

    def sleep_some(self):
        """Sleep a little to prevent multiple instances."""
        ips = self.conf_data['ENVIRONMENT']['ips']
        ip_index = ips.index(self.hostname)
        if ip_index == 1:
            sleep(10)
        elif ip_index == 2:
            sleep(20)

    def is_port_open(self, server, port=None):
        """Method to check whether a specific port on a specific host."""
        try:
            if not port:
                port = int(self.conf_data['COMMONS']['scheduler_port'][0])
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            try:
                result = sock.connect_ex((server, int(port)))
            except Exception:
                return False
            sock.close()
            if result == 0:
                return True
            else:
                return False
        except Exception:
            raise Exception

    def start_process(self, ip):
        """Method to start the Scheduler jar on a particular node."""
        port = self.conf_data['COMMONS']['scheduler_port'][0]
        username, path = get_username_path(self.conf_data, ip)
        cmd_to_start = 'nohup ' + path + '/jre/bin/java -Xms512m -Xmx512m -cp ' + path +\
            '/properties/avx-crontab.jar:' + path + \
            '/properties -Davx_logs_home=' + path + \
            '/logs -Davx_property_file_path=' + path + \
            '/properties/appviewx.properties -Dport=' + port + \
            ' -Dappviewx.property.path=' + path + \
            '/properties/ -Dlog4j.configuration=file:' + path + \
            '/properties/log4j.avx-crontab' +\
            ' com.appviewx.common.framework.jetty.Main >' +\
            path + '/logs/avx_crontab_start.log 2>&1 &'
        try:
            command = using_fabric.AppviewxShell([ip], user=username,
                                                 pty=False)
            lggr.debug('command for statrting Scheduler Jar on ' + ip)
            lggr.debug(cmd_to_start)
            l = command.run(cmd_to_start)
            key, value = l
            status = list(value)[-1][-1]
            lggr.debug('Scheduler jar command executed on ' + ip)
            return status
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def check_monitoring_process(self):
        """Function to check whether monitoring script is executing."""
        cmd_for_process_ids = "ps x | grep -i watchdog | grep -v grep " +\
            "| awk '{print $1}'"
        to_start_monitor = True
        dic_node_pid = {}
        from avx_commons import return_status_message_fabric
        from avx_commons import get_username_path
        for node in self.conf_data['ENVIRONMENT']['ips']:
            dic_node_pid[node] = []
            user, path = get_username_path(self.conf_data, node)
            fab_ob = using_fabric.AppviewxShell([node], user=user)
            ps = fab_ob.run(cmd_for_process_ids)
            stat, res = return_status_message_fabric(ps)
            if res:
                dic_node_pid[node] = dic_node_pid[node] + res.strip().split()
                to_start_monitor = False

        try:
            del dic_node_pid[self.conf_data['ENVIRONMENT']['ips'][0]][0]
        except IndexError:
            lggr.debug('watchdog not running on first node')
        cmd_to_stop = 'kill -9 '
        for node, pids in dic_node_pid.items():
            user, path = get_username_path(self.conf_data, node)
            fab_ob = using_fabric.AppviewxShell([node], user=user)
            for pid in pids:
                fab_ob.run(cmd_to_stop + str(pid))
        self.start_watchdog(to_start_monitor)

    def start_watchdog(self, to_start_monitor):
        """To start watchdog."""
        from avx_commons import return_status_message_fabric
        from avx_commons import get_username_path
        try:
            conf = ConfigObj(os.path.abspath(
                where_am_i + '/../../conf/monitor.conf'))
            try:
                to_start = conf['CONFIGURATION']['MONITOR'].lower()
            except:
                to_start = conf['CONFIGURATION']['monitor'].lower()
            if to_start != 'true':
                return
        except:
            return
        if not to_start_monitor:
            return
        for node in self.conf_data['ENVIRONMENT']['ips']:
            user, path = get_username_path(self.conf_data, node)
            cmd_to_monitor = 'nohup ' + path + '/Python/bin/python ' +\
                path + '/scripts/Commons/avx-watchdog.py ' +\
                '>/dev/null 2>&1 &'
            f_ob = using_fabric.AppviewxShell([node], user=user, pty=False)
            ps = f_ob.run(cmd_to_monitor)
            stat, res = return_status_message_fabric(ps)
            if stat:
                lggr.debug('Monitoring script started on: ' + node)
                break

    def check_vip_silo_process(self):
        """Check if silo_vip_config script file is running on all web nodes."""
        if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'false':
            return
        cmd_for_process_ids = "ps x | grep -i silo_vip | grep -v grep " +\
            "| awk '{print $1}'"
        from avx_commons import return_status_message_fabric
        from avx_commons import get_username_path
        for node in self.conf_data['WEB']['ips']:
            user, path = get_username_path(self.conf_data, node)
            fab_ob = using_fabric.AppviewxShell([node], user=user, pty=False)
            ps = fab_ob.run(cmd_for_process_ids)
            stat, res = return_status_message_fabric(ps)
            if not res:
                cmd_to_start = 'nohup ' + path + '/Python/bin/python ' +\
                    path + '/scripts/Commons/silo_vip_configuration.py' +\
                    ' >/dev/null 2>&1 &'
                fab_ob.run(cmd_to_start)

    def get_pid_kill_dummy(self):
        """Getting the pid of dummy process and killing it."""
        import subprocess
        port = self.conf_data['COMMONS']['scheduler_port'][0]
        cmd = 'netstat -tupln | grep ' + port
        px = subprocess.run(cmd,
                            shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            pid = px.stdout.decode().strip().split()[-1].split('/')[0]
        except IndexError:
            lggr.debug('No process running on port ' + port)
            pid = ''
        dummy_pids_cmd = "ps x | grep avx-crontab | grep -v grep " +\
            "| awk '{print $1}'"
        ps = subprocess.run(dummy_pids_cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        dummy_pids = ps.stdout.decode().split('\n')
        if pid in dummy_pids:
            dummy_pids.remove(pid)
        for kill_pid in dummy_pids:
            kill_cmd = 'kill -9 ' + kill_pid
            subprocess.Popen(kill_cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    def kill_process(self, ip):
        """Method to kill the Scheduler jar process on a particular node."""
        username, path = get_username_path(self.conf_data, ip)
        port = self.conf_data['COMMONS']['scheduler_port'][0]
        cmd_to_kill = path + '/Python/bin/python ' + path +\
            '/scripts/Plugins/plugin_stop.py Scheduler.jar ' + str(port)
        try:
            command = using_fabric.AppviewxShell([ip], user=username)
            command.run(cmd_to_kill)
            lggr.debug('Scheduler jar process killed on ' + ip)
            lggr.info('Scheduler jar process killed on ' + ip)
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def monitor_process(self):
        """Method to monitor the Scheduler Jar on a particular node."""
        from status_gateway import GatewayStatus
        port = self.conf_data['COMMONS']['scheduler_port'][0]
        hosts = self.conf_data['MONGODB']['ips']
        primary_ip = self.conf_data['COMMONS']['scheduler_ip'][0]
        try:
            hosts.remove(primary_ip)
        except:
            print('Scheduler IP is not present in mongo hosts.')
            lggr.error('Scheduler IP is not present in mongo hosts.')
            sys.exit(1)
        hosts.insert(0, primary_ip)
        active_hosts = []
        to_start = True

        for node in hosts:
            check_status_on_node = self.is_port_open(node, port)
            if check_status_on_node:
                if hosts.index(node) == 0:
                    lggr.debug(
                        'Scheduler jar is running on primary host: ' +
                        primary_ip)
                else:
                    lggr.debug('Scheduler jar running on ' + node)
                active_hosts.append(node)
                to_start = False
        if len(active_hosts) > 1:
            for node in active_hosts[1:]:
                self.kill_process(node)
        if to_start:
            try:
                property_file = where_am_i +\
                    '/../../properties/appviewx.properties'
                property_data = ConfigObj(property_file)
                from avx_commons import process_status
                try:
                    url = property_data['GATEWAY_BASE_URL'].rstrip('/') + '/avxmgr/api'
                    response = process_status(url)
                    if response.lower() == 'pageup':
                        gateway_status = True
                    else:
                        print(
                            'Unable to start scheduler process! avx_platform_gateway is not' +
                            ' running!')
                        return
                except:
                    print(
                        'Unable to start scheduler process! avx_platform_gateway is not' +
                        ' running!')
                    return
                # try:
                #     ipaddress.ipaddress(gateway_ip)
                # except:
                #     for ip, host in content.iteritems():
                #         if host == gateway_ip:
                #             gateway_ip = ip
                #             break
                # gateway_zip = zip(gateway_ip, gateway_port)
            except Exception:
                print('Can not read the property file')
            # ob = GatewayStatus(['--status', 'gateway'], self.conf_data)
            # gateway_status = ob.status(gateway_zip, mute=True)
            # if not gateway_status:
            #     lggr.debug(
            #         'avx_platform_gateway is not running. So unable to start scheduler' +
            #         ' process.')
            #     lggr.error(
            #         'avx_platform_gateway is not running. So unable to start scheduler' +
            #         ' process.')
            #     print(
            #         'Unable to start scheduler process! avx_platform_gateway is not' +
            #         ' running!')
            #     return
            # lggr.debug('No instance of scheduler jar running found!')
            self.mongo_exit = False
            for node in hosts:
                lggr.debug(
                    'Attempting to start scheduler jar process on ' + node)
                username, path = get_username_path(self.conf_data, node)
                if node == self.hostname or check_accessibility(
                        [username + '@' + node], self.conf_data):
                    mongo_ports = self.conf_data['MONGODB']['ports']
                    mongo_port = mongo_ports[hosts.index(node)]
                    mongo_status = self.is_port_open(node, mongo_port)
                    if not mongo_status:
                        lggr.debug('Mongo not running on: ' + node)
                        self.mongo_exit = True
                        continue
                    self.mongo_exit = False
                    res = self.start_process(node)
                    if res:
                        lggr.debug('Scheduler Jar process started on ' + node)
                        lggr.info('Scheduler Jar process started on ' + node)
                        return node

    def logstash_dir_check(self):
        try:
            import subprocess
            logstash_log_path = avx_path.appviewx_path + '/logs/logstash.log'
            cmd = 'du -sh ' + logstash_log_path
            ps = subprocess.run(cmd,
                                shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            size = ps.stdout.decode().strip().split('\t')[0][0:-1]
            if int(float(size)) > 10.0:
                if os.path.isdir(logstash_log_path + '.bak'):
                    shutil.rmtree(logstash_log_path + '.bak')
                shutil.move(logstash_log_path, logstash_log_path + '.bak')
                os.makedirs(logstash_log_path)
        except Exception:
            return

    def initialize(self):
        """."""
        self.get_pid_kill_dummy()
        try:
            if self.config['SCHEDULER']['scheduler'].lower() == 'false':
                return
        except:
            return
        self.sleep_some()
        lggr.debug('Starting the Scheduler Jar monitoring process')
        lggr.info('Starting the Scheduler Jar monitoring process')
        ip_started_on = self.monitor_process()
        if self.mongo_exit:
            print('Unable to start scheduler process! MongoDB is not running!')
        lggr.debug('Scheduler Jar monitoring completed')
        lggr.info('Scheduler Jar monitoring completed')
        if not self.mongo_exit:
            self.check_monitoring_process()
        self.check_vip_silo_process()
        self.logstash_dir_check()
        return(ip_started_on)

if __name__ == '__main__':
    try:
        ob = SchedulerMonitor()
        ob.initialize()
    except Exception as e:
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
