#!../Python/bin/python
""" Common class to perform the mainpulation of logstash operations"""
import sys
import start_logstash
import stop_logstash
import status_logstash
import avx_commons
import logger
import os
env_path=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(env_path , '../')))
from status import status
s = status()
lggr = logger.avx_logger('LOGSTASH')
import avx_commons
import monitorconfigure
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
# print (s.getStatus("logstash"))


class Logstash():

    def __init__(self, user_input, conf_data):
        lggr.debug("User input for logstash operation: %s" % user_input)
        self.user_input = user_input
        self.conf_data = conf_data
        if len(user_input) == 2:
            self.user_input.append('all')

    def logstash_start(self, logstash_nodes):
        lggr.debug("Redirect to the logstash start operation")
        lggr.info("Redirect to the logstash start operation")
        obj = start_logstash.LogstashStart(self.user_input[2:], self.conf_data)
        obj.start(logstash_nodes)

    def logstash_stop(self, logstash_nodes):
        lggr.debug("Redirect to the logstash stop operation")
        lggr.info("Redirect to the logstash stop operation")
        obj = stop_logstash.LogstashStop(self.user_input[2:], self.conf_data)
        obj.stop(logstash_nodes)

    def logstash_status(self, logstash_nodes):
        lggr.debug("Redirect to the logstash status operation")
        lggr.info("Redirect to the logstash status operation")
        obj = status_logstash.LogstashStatus(
            self.user_input[2:], self.conf_data)
        obj.status(logstash_nodes)

    def logstash_restart(self, logstash_nodes,backup_logstash_nodes):
        lggr.debug("Redirect to the logstash restart operation")
        lggr.info("Redirect to the logstash restart operation")
        obj = stop_logstash.LogstashStop(self.user_input[2:],self.conf_data)
        obj.stop(logstash_nodes)
        obj = start_logstash.LogstashStart(self.user_input[2:],self.conf_data)
        obj.start(backup_logstash_nodes)

    def operation(self):
        lggr.debug("Finding the operation of logstash(Start/Stop/Restart/Status)")
        if self.user_input[0].lower() in ['--start','--stop','--status','--restart']:
           try:
              if not self.conf_data['LOGSTASH']['syslog_receiver_enabled'][0].lower() == 'true':
                 return
           except Exception:
              return
           lggr.debug("User input for logstash start operation" % self.user_input)
           if len(self.user_input) > 4:
              avx_commons.help_fun('avx_platform_logstash',self.user_input[0])
           if len(self.user_input) <= 2:
              self.user_input.append('all')
           if len(self.user_input) == 4 and not self.user_input[2] + ':' + self.user_input[3]  in self.conf_data['LOGSTASH']['hosts']:
                 avx_commons.help_fun('avx_platform_logstash',self.user_input[0])
           logstash_ips = self.conf_data['LOGSTASH']['ips']
           if not (self.user_input[2] ==
                'all' or self.user_input[2] in logstash_ips):
              if 'operation' in self.user_input:
                return
              else:
                avx_commons.help_fun('avx_platform_logstash',self.user_input[0])
           else:
              logstash_ips = self.conf_data['LOGSTASH']['ips']
              logstash_ports = self.conf_data['LOGSTASH']['ports']
           if self.user_input[2] in logstash_ips:
              port_index = logstash_ips.index(self.user_input[2])
              logstash_ips = [self.user_input[2]]
              logstash_ports = [logstash_ports[port_index]]
           logstash_nodes = zip(logstash_ips, logstash_ports)
           backup_logstash_nodes = zip(logstash_ips, logstash_ports)
           lggr.debug("starting service for following ips : %s"  % logstash_nodes)
           nodes = self.user_input[1::]
           try:
              nodes.remove("all")
           except:
              pass
           # print (nodes)
           #if self.user_input[0].lower() in ["--start"]:
           #   if s.getStatus(nodes) == "True":
           #       self.logstash_status(logstash_nodes)
           #       return 0
           if self.user_input[0].lower() == '--start':
              self.logstash_start(logstash_nodes)
           elif self.user_input[0].lower() == '--stop':
              self.logstash_stop(logstash_nodes)
           elif self.user_input[0].lower() == '--status':
              self.logstash_status(logstash_nodes)
           elif self.user_input[0].lower() == '--restart':
              self.logstash_restart(logstash_nodes,backup_logstash_nodes)
        else:
            lggr.error("The logstash component supports only basic actions (start, stop, restart,stop)")
            lggr.error("User_input is not valid: %s " % self.user_input)

