#!/usr/bin/python
import os
import avx_commons
import using_fabric
from termcolor import colored
import socket
import logger
lggr = logger.avx_logger('MONGODB')
local_hostname = socket.gethostname()
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class MongoDBstatus():

    def __init__(self, user_input, conf_data):
        self.user_input = user_input
        self.conf_data = conf_data

    def status(self,mongodb_nodes):

        check = False
        for ip, port in mongodb_nodes:
            try:
                username, path = avx_commons.get_mongo_username_path(
                    self.conf_data, ip)
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
                continue
            response = avx_commons.port_status(ip, port)
            if not response.lower() == 'listening':
                print_statement('Database', '', ip, port, 'Not Running', '')
                continue
            if not check:
                try:
                    db = avx_commons.db_connection(self.conf_data, True)
                    member_status = db.admin.command('replSetGetStatus')
                    check = True
                except Exception as e:
                    print_statement('Database', '', ip, port, 'Not Running', '')
                    continue
            for index in range(0, len(member_status['members'])):
                if member_status['members'][index][
                        'name'] == str(ip + ":" + port) or member_status['members'][index][
                        'name'] == str(local_hostname + ':' + port):
                    if 'not reachable/healthy' in member_status[
                            'members'][index]['stateStr']:
                        print_statement('database', member_status['members'][index]['stateStr'], ip, port, 'not running')
                    else:
                        print_statement('database', member_status['members'][index]['stateStr'], ip, port, 'running')
