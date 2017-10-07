#!/ usr/bin/pthon

import os
import subprocess
import sys
from time import sleep

def execute_cmd(cmd):
    try:
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except Exception as e:
        print ("unable to execute")
        sys.exit(1)
    return ps

class IPTable:
    def rule_ipt(self):
        try:
            cmd = ["iptables -A INPUT -p tcp -s xxx.xxx.xxx.xxx -j DROP",
                   "iptables -A INPUT -p tcp -s xxx.xxx.xxx.xxx -j ACCEPT",
                   ]
            for command in cmd:
                execute_cmd(command)
        except Exception as e:
            print(e)
            sys.exit(1)






if __name__ == "__main__":
    try:
        if not int(os.getuid()) == 0:
            print ("The script should execute by root user")

    except Exception as e:
        print("exicting")
        print(e)
        sys.exit(1)




