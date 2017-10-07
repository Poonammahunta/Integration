#!/usr/bin/python
import os
import sys
from avx_commons import get_mongo_username_path
import using_fabric
import set_path
from termcolor import colored
import logger
import re
import subprocess
lggr = logger.avx_logger('MONGODB')
avx_path = set_path.AVXComponentPathSetting()
import avx_commons
import signal
from avx_commons import print_statement
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


class MongoDBStop():

    def __init__(self, user_input, conf_data):
        lggr.debug('User input for the mongo stop operation : [%s]' % user_input)
        self.user_input = user_input
        self.conf_data = conf_data

    def stop(self,mongodb_nodes):

        for ip, port in mongodb_nodes:
            lggr.debug('Stoping mongodb in %s' % ip)
            try:
                username, path = get_mongo_username_path(
                    self.conf_data, ip)
                lggr.debug('Username and path for %s are [%s,%s] ' % (ip,username,path))
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
                continue
            cmd = path + '/db/mongodb/bin/mongod --dbpath ' + \
                        path + '/db/mongodb/data/db --shutdown'

            lock_file = path + '/db/mongodb/data/db/mongod.lock' 
            rm_sock_file = 'rm -rf /tmp/mongodb*.sock'
            command = using_fabric.AppviewxShell([ip], user=username)
            lggr.debug('Command executed for stopping db for ip (%s) : %s ' % (ip,cmd))
            try:
              l = command.run(cmd)
            except Exception:
              print (colored('Error in communicating with %s' % ip,'red'))
              continue
            check_file = "if [ -f "+ lock_file + " ] ; then echo 'Present' ; fi" 
            try:
              output,status = command.run(check_file)
            except Exception:
              print (colored('Error in communicating with %s' % ip,'red'))
              continue
            l=command.run(rm_sock_file)
           
            if output == 'Present' and status:
             
                kill_cmd = 'cat ' + lock_file + ' | xargs kill -9'
                lggr.debug('Command executed for stopping db for ip (%s) : %s ' % (ip,kill_cmd))
                l = command.run(kill_cmd)
            else:
               
                lggr.debug('Lock File for Mongodb not Found . Getting the process id for Mongo')
                dbpath = avx_path.db_path
                cmd = "ps x | grep '" + dbpath + "'"
               
                try:
                    _,coutput = command.run(cmd)
                    output,status = list(coutput)[0]
                    output = output.split('\n')
                except Exception:
                    print (colored('Error in communicating with %s' % ip,'red'))
                    continue

                if len(output) > 2 and status:
                    pid = re.findall(r'^\d+',output[0])
                    killcmd = 'kill -9 ' + pid[0]
                    try:
                        l = command.run(killcmd)
                    except Exception:
                        print (colored('Error in communicating with %s' % ip,'red'))
                        continue
                   
            print_statement('database', '', ip, port, 'stopped') 
