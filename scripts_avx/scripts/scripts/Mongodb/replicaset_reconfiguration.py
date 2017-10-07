#!../Python/bin/python
# # Note : Above path should be changed if script location is changed
# #********************************************************************************************
# #
# # Copyright (C), AppViewX, Payoda Technologies
# # The script is used to configure mongodb in case of multinode setups in
# # a case when one or more node goes down.
# #
# # V 1.0 / 13 Feb 2017 / Shikhar Awasthi & Ahamed Yaser Arafath
# #               shikhar.a@appviewx.com & ahamedyaserarafath.mk@appviewx.com
# #
# #**********************************************************************************************

import os
import sys
import json
import socket
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
env_path = os.path.dirname(os.path.realpath(__file__)) + '/'
if not os.path.realpath(env_path + '/../Commons/') in sys.path:
    sys.path.append(os.path.realpath(env_path + '/../Commons/'))
from config_parser import config_parser
from avx_commons import get_db_credentials
where_am_i = os.path.dirname(os.path.realpath(__file__))
log_location = os.path.abspath(where_am_i + '/../../logs/')
AVX_Path = os.path.abspath(where_am_i + '/../../')
RotatingFileHandler(log_location + '/replicaset-reconfiguration.log', maxBytes=20, backupCount=5)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_location + '/replicaset-reconfiguration.log',
                    filemode='a',)


class MongoConfUpdate():
    """The class to take care of all operations."""

    def __init__(self):
        """Define the class variables."""
        conf_file = where_am_i + '/../../conf/appviewx.conf'
        conf_data = config_parser(conf_file)
        self.mongo_hosts = conf_data['MONGODB']['ips']
        self.mongo_ports = conf_data['MONGODB']['ports']
        self.active_nodes = []
        self.json_data = {}
        self.changes = False
        with open(where_am_i + '/../Commons/mongodbConfiguration.js', 'w+') as file:
            file.write('rs.conf()')
        self.db_user, self.db_pass, self.db_name = get_db_credentials()

    @staticmethod
    def is_port_open(server, port):
        """Check to see if mongo port is open or listening."""
        try:
            if port == ' ':
                return False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            try:
                sock.connect((server, int(port)))
                sock.close()
                return True
            except:
                sock.close()
                return False
        except Exception:
            raise Exception

    def get_active_nodes(self):
        """Get a list of all nodes which are up and running."""
        for host, port in zip(self.mongo_hosts, self.mongo_ports):
            status = self.is_port_open(host, port)
            if status:
                self.active_nodes.append(host)
        if not len(self.active_nodes):
            logging.debug('No DB nodes are up.')
            return False
        else:
            logging.debug(
                'Currently up MongoDB nodes: ' + ', '.join(self.active_nodes))
        return True

    def get_rs_conf_json(self):
        """Function to get the json from active dbs."""
        host = self.active_nodes[0]
        index = self.mongo_hosts.index(host)
        port = self.mongo_ports[index]
        cmd = AVX_Path + '/db/mongodb/bin/mongo --port ' +\
            port + ' ' + self.db_name + ' -u ' + self.db_user + ' -p ' +\
            self.db_pass + '  --host ' + host +\
            ' < ' + AVX_Path + '/scripts/Commons/mongodbConfiguration.js'
        ps = subprocess.run(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        data = ps.stdout.decode()
        try:
            data = data.split('bye')[0]
        except:
            pass
        index = data.find('{')
        data = data[index:]
        self.json_data = json.loads(data)

    def edit_json_data(self):
        """Edit the json data from rs.conf()."""
        members = []
        for key, value in self.json_data.items():
            if key.lower() == 'members':
                members = self.json_data['members']
                for i in range(len(members)):
                    ip, port = self.json_data['members'][i]['host'].split(':')
                    if ip in self.active_nodes:
                        value = self.json_data['members'][i]['votes']
                        value_to_set = 1
                        self.json_data['members'][i]['votes'] = value_to_set
                        if str(value) != str(value_to_set):
                            self.changes = True
                    else:
                        value = self.json_data['members'][i]['votes']
                        value_to_set = 0
                        self.json_data['members'][i]['votes'] = value_to_set
                        if str(value) != str(value_to_set):
                            self.changes = True
        self.json_data = json.dumps(self.json_data)

    def create_js_file(self):
        """Create the js file to push into mongodb."""
        with open(where_am_i + '/../Commons/mongodbConfiguration.js', 'w+') as file:
            file.write('a=' + self.json_data + '\n')
            file.write('rs.reconfig(a,{force:true})')

    def push_changes(self):
        """Push the final changes into MongoDB."""
        host = self.active_nodes[0]
        index = self.mongo_hosts.index(host)
        port = self.mongo_ports[index]
        cmd = AVX_Path + '/db/mongodb/bin/mongo --port ' +\
            port + ' ' + self.db_name + ' -u ' + self.db_user + ' -p ' +\
            self.db_pass + '  --host ' + host +\
            ' < ' + AVX_Path + '/scripts/Commons/mongodbConfiguration.js'
        subprocess.run(cmd, shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    def initialize(self):
        """Start the process."""
        logging.debug('#' * 80)
        logging.debug('')
        logging.debug(
            'Starting MongoDB replicaset reconfiguration monitoring at: ' +
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        if not self.get_active_nodes():
            return
        self.get_rs_conf_json()
        self.edit_json_data()
        self.create_js_file()
        if self.changes:
            logging.debug('Reconfiguring the MongoDB')
            self.push_changes()
        else:
            logging.debug('No need to reconfigure MongoDB')
        os.remove(AVX_Path + '/scripts/Commons/mongodbConfiguration.js')
        logging.debug('')
        logging.debug('#' * 80 + '\n\n')


if __name__ == '__main__':
    ob = MongoConfUpdate()
    ob.initialize()
