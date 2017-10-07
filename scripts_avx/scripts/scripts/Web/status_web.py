#!/usr/bin/python
import os
import sys
import avx_commons
import using_fabric
from termcolor import colored
import logger
from avx_commons import print_statement
lggr = logger.avx_logger('WEB')
current_file_path = os.path.dirname(os.path.realpath(__file__))


class WebStatus():

    def __init__(self, user_input, conf_data):
        self.user_input = user_input
        self.base_url = '/web/login'
        self.conf_data = conf_data
        self.web_version = 'v' + self.conf_data['COMMONS']['version'][0]

    def status(self, web_nodes):
        self.web_vip_status()
        for ip, port in web_nodes:
            try:
                username, path = avx_commons.get_username_path(
                    self.conf_data, ip)
            except Exception:
                lggr.error("Error in getting username and path for %s" % ip)
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
            url = "http://" + ip + ":" + port
            try:
                if self.conf_data['WEB']['appviewx_web_https'][0].lower() == 'true':
                    url = "https://" + ip + ":" + port
            except Exception:
                pass
            url_response = avx_commons.process_status(url)
            if url_response.lower() == 'pageup':
                    print_statement('Web', self.web_version, ip, port, 'Running')
            else:
                    response = avx_commons.port_status(ip, port)
                    if response.lower() == 'listening':
                        print_statement('Web', self.web_version, ip, port, 'Not Accessible')
                    else:
                        print_statement('Web', self.web_version, ip, port, 'Not Running')

    def web_vip_status(self):
      if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'true' and self.conf_data['WEB']['web_vip_enabled'][0].lower() == 'true':
       try:
           ip,port = self.conf_data['WEB']['appviewx_web_vip'][0].split(':')
       except:
           print (colored('APPVIEWX_WEB_VIP(%s) - (IP format) under WEB section is not valid' % self.conf_data['WEB']['appviewx_web_vip'][0],'red'))
           return
       url = "http://" + ip + ":" + port
       try:
            if self.conf_data['WEB']['appviewx_web_vip_https'][0].lower() == 'true':
               url = "https://" + ip + ":" + port
       except Exception:
            pass
       url_response = avx_commons.process_status(url)
       if url_response.lower() == 'pageup':
            print_statement('Web', self.web_version, ip, port, 'Running','VIP')
       else:
            response = avx_commons.port_status(ip, port)
            if response.lower() == 'listening':
                print_statement('Web', self.web_version, ip, port, 'Not Accessible','VIP')
            else:
                print_statement('Web', self.web_version, ip, port, 'Not Running','VIP')

if __name__ == '__main__':

    user_input = sys.argv[2:]
    obj = WebStatus(user_input)
    obj.status()

