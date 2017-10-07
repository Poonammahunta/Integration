import logging
import os
import sys
import socket
from time import sleep
import traceback

def set_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler('hello.log')
    handler.setLevel(logging.INFO)

# create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

# add the handlers to the logger
    logger.addHandler(handler)
    return logger

class PreCheck:
    
    def disk_space(self):
         lggr = set_logging()
         try:
            total_size = int(os.popen("df -hT .| awk '{print $3}'").read().split()[1][:-1])
            used_size =  int(os.popen("df -hT .| awk '{print $4}'").read().split()[1][:-1])
            avail_size = int(os.popen("df -hT .| awk '{print $5}'").read().split()[1][:-1])
            #lggr.info("#############")
            #lggr.info('total size %s' % total_size ,'used size %s' % used_size ,'avail size %s ' % avail_size)
            lggr.info(" \n Total Size:%s \n Used Size:%s \n Avail Size:%s" %(total_size, used_size, avail_size))

            if avail_size < 200:
                lggr.error("available size is not matching for application")
                error = str('\n'.join())

         except KeyboardInterrupt:
             print('Keyboard Interrupt')
             sys.exit(1)

         except Exception as e:
             lggr.debug('issue in disk alert')


    def set_host(self):
        lggr = set_logging()
        try:
            hostname = socket.gethostbyname(socket.gethostname())
            host_ip = os.popen("hostname -i").read()
            lggr.info("Hostname : %s Host_ip : %s" %(hostname,host_ip))
            if not hostname:
                lggr.error("Hostname not set: ")
            elif not host_ip:
                lggr.error("Hostip not set: ")
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            sys.exit(1)

        
    def port_open(self):
        lggr = set_logging()
    
        port_opened = []
        port_check = ['80','443','64633','49676','61460']
        port_open = os.popen("netstat -n | grep 443 |awk '{print $3}'").read().splitlines()
        for port in port_open:
            if port.split(':')[1] in port_check:
                port_opened.append(port.split(':')[1])
        print port_opened    
        try:
            for port in port_check:
                for port1 in port_opened:
                    if port == port1:
                        #print port
                        #lggr.error("#############")
                        lggr.error("The port is opened for other application %s" %(port))
                    else:
                        continue
                    continue
            
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            sys.exit(1)
        except Exception as e:
            lggr.info("ports are available for the application")


    def main(self):
         self.port_open()
         self.set_host()
         self.disk_space()
                


                
if __name__ =="__main__":
    ob = PreCheck()
    ob.main()
   
        
