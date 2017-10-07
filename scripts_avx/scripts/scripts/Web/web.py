#!../Python/bin/python
""" Common class to perform the mainpulation of web operations"""
import sys
import os
import start_web
import stop_web
import status_web
import avx_commons
import logger
env_path=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(env_path , '../')))
from status import status
s = status()
lggr = logger.avx_logger('WEB')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import monitorconfigure
class Web():

    def __init__(self, user_input, conf_data):
        lggr.debug("User input for web operation: %s" % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def web_start(self, web_nodes):
        lggr.debug("Redirect to the web start operation")
        lggr.info("Redirect to the web start operation")
        obj = start_web.WebStart(self.user_input[2:], self.conf_data)
        obj.start(web_nodes)

    def web_stop(self,web_nodes):
        lggr.debug("Redirect to the web stop operation")
        lggr.info("Redirect to the web stop operation")
        obj = stop_web.WebStop(self.user_input[2:], self.conf_data)
        obj.stop(web_nodes)

    def web_status(self, web_nodes):
        lggr.debug("Redirect to the web status operation")
        lggr.info("Redirect to the web status operation")
        obj = status_web.WebStatus(self.user_input[2:], self.conf_data)
        obj.status(web_nodes)

    def web_restart(self, web_nodes,backup_web_nodes):
        lggr.debug("Redirect to the web restart operation")
        lggr.info("Redirect to the web restart operation")
        obj = stop_web.WebStop(self.user_input[2:],self.conf_data)
        obj.stop(web_nodes)
        obj = start_web.WebStart(self.user_input[2:],self.conf_data)
        obj.start(backup_web_nodes)

    def operation(self):
        if self.user_input[0] in ['--start','--stop','--status','--restart']:
           lggr.debug("User input for web stop operation" % self.user_input)
           if self.user_input[1] == 'operation' and not self.user_input[2] in self.conf_data['WEB']['ips']:
              return True
           if len(self.user_input) > 4:
              avx_commons.help_fun('avx_platform_web',self.user_input[0])
           if len(self.user_input) <= 2 :
              self.user_input.append('all')
           if len(self.user_input) == 4 and not self.user_input[2] + ':' + self.user_input[3]  in self.conf_data['WEB']['hosts']:
                 avx_commons.help_fun('avx_platform_web',self.user_input[0])
           web_ips = self.conf_data['WEB']['ips']
           if not (self.user_input[2] == 'all' or self.user_input[2] in web_ips):
              avx_commons.help_fun('avx_platform_web',self.user_input[0])
           else:
              web_ips = self.conf_data['WEB']['ips']
              web_ports = self.conf_data['WEB']['ports']
           if self.user_input[2] in web_ips:
            port_index = web_ips.index(self.user_input[2])
            web_ips = [self.user_input[2]]
            web_ports = [web_ports[port_index]]

           web_nodes = zip(web_ips, web_ports)
           backup_web_nodes = zip(web_ips, web_ports)
           lggr.debug("stoping web for the following ips : %s"  % web_nodes)
           nodes = self.user_input[1::]
           try:
              nodes.remove("all")
           except:
              pass
           # print (nodes)
           if self.user_input[0].lower() in ["--start"]:
              if s.getStatus(nodes) == "True":
                  self.web_status(web_nodes)
                  return 0

           if self.user_input[0].lower() == '--start':
              self.web_start(web_nodes)
           elif self.user_input[0].lower() == '--stop':
              self.web_stop(web_nodes)
           elif self.user_input[0].lower() == '--status':
              self.web_status(web_nodes)
           elif self.user_input[0].lower() == '--restart':
              self.web_restart(web_nodes,backup_web_nodes)
        else:
            lggr.error("The WEB component supports only basic actions (start, stop, restart,stop)")
            lggr.error("User_input is not valid: %s " % self.user_input)
            avx_commons.help_fun('avx_platform_web','--start/--stop/--restart/--status')


if __name__ == '__main__':

    user_input = sys.argv
    web_obj = web(user_input[1:])
    web_obj.operation()
