f1 = open("D:\\POO\\Py_work\\test\\old.txt","r")
f2 = open("D:\\POO\\Py_work\\test\\new.txt","w")
import re
import sys
s = raw_input("Enter the string to replace: ")
t = raw_input("Enter the string fpr replacing: ")

try:
    def sed(f1,f2,t,s):
        for item in f1.readlines():
            if s in item:
                f2.write(re.sub(s,t,item))
            else:
                f2.write(item)
        return f2
except:
    print "Error encountered"
    f2.close()
                      
                
sed(f1,f2,t,s)    
f1.close()
f2.close()
