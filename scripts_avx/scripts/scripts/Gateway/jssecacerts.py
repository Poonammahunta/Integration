#!/usr/bin/python
import os
import sys
import subprocess
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_path + '/../Commons')
import avx_commons
import using_fabric
import set_path
import socket
import getpass
from avx_commons import get_username_path
from termcolor import colored
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_path + '/../Commons')
localhost = socket.gethostbyname(socket.gethostname())
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('GATEWAY')
from config_parser import config_parser
import fabric
from fabric.api import *
fabric.state.output['warnings'] = False
fabric.state.output['output'] = False
fabric.state.output['running'] = False
fabric.state.output['everything'] = False
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def put_file(localpath, remotepath):
    try:
        get(remotepath,localpath)
    except:
        lggr.debug('Unable to download file: ' + localpath)


def put_file_remote(localpath, remotepath):
    try:
        put(localpath,remotepath)
    except:
        lggr.debug('Unable to send file: ' + localpath)

class Jssecacerts_Creator():
      def __init__(self,conf_data):
          self.conf_data = conf_data

      def initialize(self):
         local_username=getpass.getuser()
         local_path = avx_path.appviewx_path
         hosts = self.conf_data['GATEWAY']['ips']
         delete_cmd = avx_path.appviewx_path + '/jre/bin/keytool -delete -alias ' + localhost + ' -storepass changeit -keystore ' + avx_path.appviewx_path +'/jre/lib/security/jssecacerts'
         cmd =avx_path.appviewx_path + '/jre/bin/keytool -import -noprompt -trustcacerts -file ' + avx_path.appviewx_path + '/server.crt -alias ' + localhost + ' -storepass changeit -keystore ' + avx_path.appviewx_path + '/jre/lib/security/jssecacerts'
         command = using_fabric.AppviewxShell(
                [localhost], user=local_username, pty=False)
         l = command.run(delete_cmd)
         l = command.run(cmd)
         from avx_commons import get_username_path
         for host in hosts:
           ip = host
           username, path = get_username_path(self.conf_data, ip)
           if not ip == localhost:
             delete_cmd = path + '/jre/bin/keytool -delete -alias ' + ip + ' -storepass changeit -keystore ' + path +'/jre/lib/security/jssecacerts'
             cmd = path + '/jre/bin/keytool -import -noprompt -trustcacerts -file ' + path + '/server.crt -alias ' + ip + ' -storepass changeit -keystore ' + path + '/jre/lib/security/jssecacerts'
             command = using_fabric.AppviewxShell(
                [ip], user=username, pty=False)
             try:
                l = command.run(delete_cmd)
                l = command.run(cmd)
             except Exception:
                print (colored('Error in communicating with %s' % ip,'red'))
                continue
             port = str(self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(ip)])
             execute(put_file,localpath = local_path + '/jre/lib/security/jssecacerts_tmp',remotepath = path + '/jre/lib/security/jssecacerts', hosts =username + '@' + ip + ':' + port)
           if not ip == localhost:
             command = using_fabric.AppviewxShell(
                [localhost], user=local_username, pty=False)
             merge_command = local_path + '/jre/bin/keytool -importkeystore -noprompt -srckeystore ' + local_path + '/jre/lib/security/jssecacerts_tmp -destkeystore ' + local_path + '/jre/lib/security/jssecacerts -destkeystore ' + local_path + '/jre/lib/security/jssecacerts -srcstorepass changeit -deststorepass changeit'
             l = command.run(merge_command)

         cacerts_merge_cmd = 'echo -e "\n" | ' + local_path + '/jre/bin/keytool -importkeystore -noprompt -srckeystore ' +\
             local_path + '/jre/lib/security/cacerts -destkeystore ' +\
             local_path + '/jre/lib/security/jssecacerts -destkeystore ' +\
             local_path + '/jre/lib/security/jssecacerts -deststorepass changeit'
         ps = subprocess.run(cacerts_merge_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
         if ps.returncode:
            print('Unable to merge cacerts to jssecacerts!!')
            lggr.error('Unable to merge cacerts to jssecacerts!!')

         all_hosts = self.conf_data['ENVIRONMENT']['ips'] * 1
         all_hosts.remove(localhost)

         for host in all_hosts:
             ip = host
             username, path = get_username_path(self.conf_data, ip)
             port = str(self.conf_data['ENVIRONMENT']['ssh_port'][self.conf_data['ENVIRONMENT']['ips'].index(ip)])
             if not ip == localhost:
                execute(put_file_remote,localpath = local_path+ '/jre/lib/security/jssecacerts',remotepath = path + '/jre/lib/security/jssecacerts', hosts = username + '@' + ip + ':' + port)
  
