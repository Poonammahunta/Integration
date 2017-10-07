#!../Python/bin/python
""" Common class to perform the mainpulation of gateway operations"""
import sys
import start_gateway
import stop_gateway
import status_gateway
import avx_commons
import logger
import os
env_path=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(env_path , '../')))
from status import status
s = status()
lggr = logger.avx_logger('GATEWAY')
import avx_commons
import monitorconfigure
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
# print (s.getStatus("gateway"))
class Gateway():

    def __init__(self, user_input, conf_data):
        lggr.debug("User input for gateway operation: %s" % user_input)
        self.user_input = user_input
        self.conf_data = conf_data
        if len(user_input) == 2:
            self.user_input.append('all')

    def gateway_start(self, gateway_nodes):
        lggr.debug("Redirect to the gateway start operation")
        lggr.info("Redirect to the gateway start operation")
        obj = start_gateway.GatewayStart(self.user_input[2:], self.conf_data)
        obj.start(gateway_nodes)

    def gateway_stop(self, gateway_nodes):
        lggr.debug("Redirect to the gateway stop operation")
        lggr.info("Redirect to the gateway stop operation")
        obj = stop_gateway.GatewayStop(self.user_input[2:], self.conf_data)
        obj.stop(gateway_nodes)

    def gateway_status(self, gateway_nodes):
        lggr.debug("Redirect to the gateway status operation")
        lggr.info("Redirect to the gateway status operation")
        obj = status_gateway.GatewayStatus(
            self.user_input[2:], self.conf_data)
        obj.status(gateway_nodes)

    def gateway_restart(self, gateway_nodes,backup_gateway_nodes):
        lggr.debug("Redirect to the gateway restart operation")
        lggr.info("Redirect to the gateway restart operation")
        obj = stop_gateway.GatewayStop(self.user_input[2:],self.conf_data)
        obj.stop(gateway_nodes)
        obj = start_gateway.GatewayStart(self.user_input[2:],self.conf_data)
        obj.start(backup_gateway_nodes)

    def operation(self):
        lggr.debug("Finding the operation of Gateway(Start/Stop/Restart/Status)")
        if self.user_input[0].lower() in ['--start','--stop','--status','--restart']:
           lggr.debug("User input for gateway start operation" % self.user_input)
           if len(self.user_input) > 4:
              avx_commons.help_fun('avx_platform_gateway',self.user_input[0])
           if len(self.user_input) <= 2:
              self.user_input.append('all')
           if len(self.user_input) == 4 and not self.user_input[2] + ':' + self.user_input[3]  in self.conf_data['GATEWAY']['hosts']:
                 avx_commons.help_fun('avx_platform_gateway',self.user_input[0])
           gateway_ips = self.conf_data['GATEWAY']['ips']
           if not (self.user_input[2] ==
                'all' or self.user_input[2] in gateway_ips):
              if 'operation' in self.user_input:
                return
              else:
                avx_commons.help_fun('avx_platform_gateway',self.user_input[0])
           else:
              gateway_ips = self.conf_data['GATEWAY']['ips']
              gateway_ports = self.conf_data['GATEWAY']['ports']
           if self.user_input[2] in gateway_ips:
              port_index = gateway_ips.index(self.user_input[2])
              gateway_ips = [self.user_input[2]]
              gateway_ports = [gateway_ports[port_index]]
           gateway_nodes = zip(gateway_ips, gateway_ports)
           backup_gateway_nodes = zip(gateway_ips, gateway_ports)
           lggr.debug("starting service for following ips : %s"  % gateway_nodes)
           nodes = self.user_input[1::]
           try:
              nodes.remove("all")
           except:
              pass
           # print (nodes)
           if self.user_input[0].lower() in ["--start"]:
              if s.getStatus(nodes) == "True":
                  self.gateway_status(gateway_nodes)
                  return 0
           if self.user_input[0].lower() == '--start':
              self.gateway_start(gateway_nodes)
           elif self.user_input[0].lower() == '--stop':
              self.gateway_stop(gateway_nodes)
           elif self.user_input[0].lower() == '--status':
              self.gateway_status(gateway_nodes)
           elif self.user_input[0].lower() == '--restart':
              self.gateway_restart(gateway_nodes,backup_gateway_nodes)
        else:
            lggr.error("The GATEWAY component supports only basic actions (start, stop, restart,stop)")
            lggr.error("User_input is not valid: %s " % self.user_input)

