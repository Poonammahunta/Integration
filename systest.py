temp = "D:\python_work\CDL_Break_74.xml"
import sys
import re
f = open("D:\python_work\poonam\CDL_TransmissionECM_51.xml","r")
d = {}
w = "<vbench>\n+<module "

def poo(f):
    for line in f.readlines():
        result = re.findall(r'pid= "\d[0-9]|pid= "\w*"| value= "\d[0-9]*"',line)
        print result     
        
        
        
        

poo(f)        
