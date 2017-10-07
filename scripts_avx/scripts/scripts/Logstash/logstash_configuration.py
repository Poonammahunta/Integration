#!../../Python/bin/python
"""Script to initialize logstash."""
import os
import sys
from termcolor import colored
import socket
import subprocess
current_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, current_file_path + '/../Commons')
from avx_commons import execute_on_particular_ip
from avx_commons import run_local_cmd
from initialize_common import InitializeCommon
import logger
import set_path
avx_path = set_path.AVXComponentPathSetting()
lggr = logger.avx_logger('initialize_logstash')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
localhost=socket.gethostbyname(socket.gethostname())

class Logstashconfiguration():
    """Class to initialize logstash."""

    def __init__(self):
        """."""
        try:
            from config_parser import config_parser
            self.path =avx_path.appviewx_path
            self.conf_file = current_file_path + '/../../conf/appviewx.conf'
            self.conf_data = config_parser(self.conf_file)
            self.hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            print(colored(e, 'red'))
            lggr.error(e)
            sys.exit(1)



    def input_file_content(self):
       try:
        with open(avx_path.appviewx_path + '/logstash/conf_templates/template_Input.conf', 'r') as create_file:
             input_template = create_file.read()
        input_template=input_template.replace("{HOST}",localhost)
        port_index = self.conf_data['LOGSTASH']['ips'].index(localhost)
        input_template=input_template.replace("{PORT}",self.conf_data['LOGSTASH']['ports'][port_index])
         
        with open(avx_path.appviewx_path + '/logstash/conf.d/Input.conf', 'w') as create_file:
             create_file.write(input_template)
       except Exception as e:
           print (colored('Error in configuring Output.conf : %s' % e,'red'))
           lggr.error('Error in configuring Output.conf')
           pass

    def output_file_content(self):
      try:
        with open(avx_path.appviewx_path + '/logstash/conf_templates/template_Output.conf', 'r') as create_file:
             output_template = create_file.read()
        if self.conf_data['ENVIRONMENT']['multinode'][0].lower() == 'false':
           if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'https')
           else:
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'http')
           output_template=output_template.replace("{GATEWAY_IP}",self.conf_data['GATEWAY']['ips'][0])
           output_template=output_template.replace("{GATEWAY_PORT}",self.conf_data['GATEWAY']['ports'][0])
           output_template=output_template.replace("{GW_KEY}",self.conf_data['GATEWAY']['appviewx_gateway_key'][0])
        else:
           if self.conf_data['GATEWAY']['gateway_vip_enabled'][0].lower() == 'true':
            if self.conf_data['GATEWAY']['appviewx_gateway_vip_https'][0].lower() == 'true':
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'https')
            else:
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'http')
            try:
             ip,port = self.conf_data['GATEWAY']['appviewx_gateway_vip'][0].split(':')
            except Exception:
             print (colored('APPVIEWX_GATEWAY_VIP field under GATEWAY section is not valid','red'))
           else:
             if self.conf_data['GATEWAY']['appviewx_gateway_https'][0].lower() == 'true':
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'https')
             else:
               output_template=output_template.replace("{GATEWAY_VIP_HTTP}",'http')
             if localhost in self.conf_data['GATEWAY']['ips']:
                ip_index = self.conf_data['GATEWAY']['ips'].index(localhost)
                port = self.conf_data['GATEWAY']['ports'][ip_index]
                ip = localhost
             else:
                ip = self.conf_data['GATEWAY']['ips'][0]
                port = self.conf_data['GATEWAY']['ports'][0]
             
           output_template=output_template.replace("{GATEWAY_IP}",ip)
           output_template=output_template.replace("{GATEWAY_PORT}",port)
           output_template=output_template.replace("{GW_KEY}",self.conf_data['GATEWAY']['appviewx_gateway_key'][0])
        with open(avx_path.appviewx_path + '/logstash/conf.d/Output.conf', 'w') as create_file:
             create_file.write(output_template)
      except Exception as e:
           print (e)
           print (colored('Error in configuring Output.conf : %s' % e,'red'))
           lggr.error('Error in configuring Output.conf')
           pass
  
    def pattern_file_content(self):
        try:
           with open(avx_path.appviewx_path + '/logstash/conf_templates/template_F5.conf', 'r') as create_file:
                pattern_data = create_file.read()
           pattern_data = pattern_data.replace('{PATTERN_DIR}',avx_path.appviewx_path + '/logstash/patterns/')
           with open(avx_path.appviewx_path + '/logstash/conf.d/F5.conf', 'w') as create_file:
             create_file.write(pattern_data)
        except Exception as e:
           print (colored('Error in configuring pattern directory entry in F5.conf : %s' % e,'red'))
           lggr.error('Error in configuring pattern directory entry in F5.conf')
           pass 
    
    def logstash_setup(self):
        try:
           with open(avx_path.appviewx_path + '/logstash/config/logstash.yml','r') as create_file:
                ls_conf_data = create_file.readlines()
           final_data = []
           if localhost in self.conf_data['LOGSTASH']['ips']:
             with open(avx_path.appviewx_path + '/logstash/config/logstash.yml', 'w') as create_file:
              for line in ls_conf_data:
               if line.startswith('http.port:'):
                  index = self.conf_data['LOGSTASH']['ips'].index(localhost)
                  line = 'http.port: '  + self.conf_data['LOGSTASH']['ports'][index] + '\n'
               if line.startswith('log.level:'):
                  try:
                     if len(self.conf_data['LOGSTASH']['log_level'][0]) == 0:
                        raise Exception
                     line = 'log.level: '  + self.conf_data['LOGSTASH']['log_level'][0].lower() + '\n'
                  except Exception:
                     line = 'log.level: info\n'
               if line.startswith('path.logs:'):
                     line = 'path.logs: ' + avx_path.appviewx_path + '/logs/logstash.log\n'
               create_file.write(line)
        except Exception as e:
               print (e)
               print (colored('Error in configuring logstash.yml : %s' % e,'red'))
               lggr.error('Error in configuring logstash.yml')
               pass


    def initialize(self):
        self.input_file_content()
        self.output_file_content()
        self.pattern_file_content()
        self.logstash_setup()

if __name__ == '__main__':
    try:
        obj = Logstashconfiguration()
        flag = obj.initialize()
    except Exception as e:
        print(colored(e, 'red'))
        sys.exit(1)

