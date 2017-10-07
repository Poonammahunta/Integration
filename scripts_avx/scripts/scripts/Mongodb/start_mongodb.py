#!/usr/bin/python
import os
import sys
import set_path
import using_fabric
import avx_commons
import socket
from termcolor import colored
hostname = socket.gethostbyname(socket.gethostname())
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('MONGODB_START')
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class MongoDBStart():

    def __init__(self, user_input, conf_data, auth=True):
        lggr.debug('User input for the mongo start operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data
        self.auth = auth

    def start(self, mongodb_nodes):
        for ip, port in mongodb_nodes:
            lggr.debug('Mongodb starting in %s' % ip)
            member = 'secondary'
            try:
                if ip + ":" + port in self.conf_data[
                        'MONGODB']['arbiter_hosts']:
                    member = 'arbiter'
            except Exception:
                continue
            try:
                username, path = avx_commons.get_mongo_username_path(
                    self.conf_data, ip)
                lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
                continue
            rm_sock_file = 'rm -rf /tmp/mongodb*.sock'
            kill_cmd = 'cat ' + path + '/db/mongodb/data/db/mongod.lock | xargs kill -9'
            empty_file = '>' + path + '/db/mongodb/data/db/mongod.lock '
            if not self.auth:
                if member == 'arbiter':
                    lggr.debug('Starting mongodb without authentication and as arbiter for %s ' % ip)
                    cmd = path + "/db/mongodb/bin/mongod --fork --port " + port + " --dbpath " + path + "/db/mongodb/data/db" + \
                        " --nojournal --replSet rpset --oplogSize 10240 --logpath " + path + "/logs/db.log" + " --maxConns 20000 --nohttpinterface --smallfiles"
                else:
                    lggr.debug('Starting mongodb without authentication for %s ' % ip)
                    cmd = path + "/db/mongodb/bin/mongod --fork --port " + port + " --dbpath " + path + "/db/mongodb/data/db" + \
                        " --nojournal --replSet rpset --oplogSize 10240 --logpath " + path + "/logs/db.log" + " --maxConns 20000 --nohttpinterface"
            else:
                if member == 'arbiter':
                    lggr.debug('Starting mongodb with authentication and as arbiter for %s ' % ip)
                    cmd = path + "/db/mongodb/bin/mongod --fork  --auth --keyFile " + path + "/db/mongodb/keyfile --port " + port + " --dbpath " + path + "/db/mongodb/data/db" + \
                        " --nojournal --replSet rpset --oplogSize 10240 --logpath " + path + "/logs/db.log" + " --maxConns 20000 --nohttpinterface --smallfiles"
                else:
                    lggr.debug('Starting mongodb with authentication for %s ' % ip)
                    cmd = path + "/db/mongodb/bin/mongod --fork  --auth --keyFile " + path + "/db/mongodb/keyfile --port " + port + " --dbpath " + path + \
                        "/db/mongodb/data/db" + " --nojournal --replSet rpset --oplogSize 10240 --logpath " + path + "/logs/db.log" + " --maxConns 20000 --nohttpinterface"

            command = using_fabric.AppviewxShell([ip], user=username)
            try:
              lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,rm_sock_file))
              l = command.run(rm_sock_file) 
              lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,kill_cmd))
              l = command.run(kill_cmd)
              lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,empty_file))
              l = command.run(empty_file)
            except Exception:
              print (colored('Error in communicating with %s' % ip,'red'))
              continue
            lggr.debug('Command executed for starting db for ip (%s) : %s ' % (ip,cmd))
            l = command.run(cmd)
            lggr.debug('Result of mongodb started operation for ip (%s): %s' % (ip,l))
            print_statement('database', '', ip, port, 'starting')

