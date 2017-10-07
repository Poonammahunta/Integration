#!../Python/bin/python
""" Common class to perform the mainpulation of mongodb operations"""
import importlib
import sys
import os
import avx_commons
import start_mongodb
import stop_mongodb
import status_mongodb
import logger
env_path=os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(env_path , '../')))
from status import status
s = status()
lggr = logger.avx_logger('MONGODB')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import monitorconfigure
import replicaset_reconfiguration
import time

class MongoDB():

    def __init__(self, user_input, conf_data, auth=True):
        lggr.debug("User input for mongodb operation: %s with auth(%s)" % (user_input, auth))
        self.user_input = user_input
        self.conf_data = conf_data
        # print(conf_data['MONGODB'])
        self.auth = auth
        if len(self.user_input) == 2:
            self.user_input.append('all')
        self.mongo_obj = replicaset_reconfiguration.MongoConfUpdate()

    def db_start(self, mongodb_nodes):
        lggr.debug("Redirect to the mongodb start operation")
        lggr.debug("Redirect to the mongodb start operation")
        obj = start_mongodb.MongoDBStart(
            self.user_input[2:],
            self.conf_data, self.auth)
        obj.start(mongodb_nodes)

    def db_restart(self, mongodb_nodes,backup_mongodb_nodes):
        backup_nodes = mongodb_nodes
        lggr.debug("Redirect to the mongodb restart operation")
        lggr.info("Redirect to the mongodb restart operation")
        obj = stop_mongodb.MongoDBStop(self.user_input[2:], self.conf_data)
        obj.stop(mongodb_nodes)
        obj = start_mongodb.MongoDBStart(
            self.user_input[2:],
            self.conf_data, self.auth)
        obj.start(backup_mongodb_nodes)

    def db_stop(self, mongodb_nodes):
        lggr.debug("Redirect to the mongodb stop operation")
        lggr.debug("Redirect to the mongodb stop operation")
        obj = stop_mongodb.MongoDBStop(self.user_input[2:], self.conf_data)
        obj.stop(mongodb_nodes)

    def db_status(self, mongodb_nodes):
        lggr.debug("Redirect to the mongodb status operation")
        lggr.debug("Redirect to the mongodb status operation")
        obj = status_mongodb.MongoDBstatus(
            self.user_input[2:], self.conf_data)
        obj.status(mongodb_nodes)

    def operation(self):
        # print(self.conf_data['MONGODB'])
        if self.user_input[0] in ['--start','--stop','--restart','--status']:
           lggr.debug("User input for mongodb start operation: %s with auth(%s)" % (self.user_input, self.auth))
           lggr.info("User input for mongodb start operation: %s with auth(%s)" % (self.user_input, self.auth))
           if self.user_input[1] == 'operation' and not self.user_input[2] in self.conf_data['MONGODB']['ips']:
              return True
           if len(self.user_input) > 4:
              avx_commons.help_fun('avx_platform_mongodb',self.user_input[0])
           if len(self.user_input) <= 2:
              self.user_input.append('all')
           if len(self.user_input) == 4 and not self.user_input[2] + ':' + self.user_input[3]  in self.conf_data['MONGODB']['hosts']:
                 avx_commons.help_fun('avx_platform_mongodb',self.user_input[0])
           mongodb_ips = self.conf_data['MONGODB']['ips']
           if not (self.user_input[2] ==
                'all' or self.user_input[2] in mongodb_ips):
              avx_commons.help_fun('avx_platform_mongodb',self.user_input[0])
           else:
              mongodb_ips = self.conf_data['MONGODB']['ips']
              mongodb_ports = self.conf_data['MONGODB']['ports']
           if self.user_input[2] in mongodb_ips:
              port_index = mongodb_ips.index(self.user_input[2])
              mongodb_ips = [self.user_input[2]]
              mongodb_ports = [mongodb_ports[port_index]]
           mongodb_nodes = zip(mongodb_ips, mongodb_ports)
           backup_mongodb_nodes = zip(mongodb_ips, mongodb_ports)
           lggr.debug("Finding the operation of db(Start/Stop/Restart/Status)")
           nodes = self.user_input[1::]
           try:
              nodes = list(filter(("all").__ne__, nodes))
           except:
              pass
           # print (nodes)
           if self.user_input[0].lower() in ["--start"]:
              if "mongodb" not in nodes:
                  nodes.insert(0, 'mongodb')
              if self.auth:
                if s.getStatus(nodes) == "True":
                  self.db_status(mongodb_nodes)
                  return 0
           if self.user_input[0].lower() == '--start':
              self.db_start(mongodb_nodes)
           elif self.user_input[0].lower() == '--stop':
              self.db_stop(mongodb_nodes)
           elif self.user_input[0].lower() == '--restart':
              self.db_restart(mongodb_nodes,backup_mongodb_nodes)
           elif self.user_input[0].lower() == '--status':
              self.db_status(mongodb_nodes)
        else:
            lggr.error("The DB command supports only basic actions (start, stop, restart,stop)")
            lggr.error("User_input is not valid: %s " % self.user_input)
            avx_commons.help_fun('avx_platform_mongodb','--start/--stop/--restart/--status')
