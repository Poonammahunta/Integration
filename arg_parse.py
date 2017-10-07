# p1.py
import sys
import subprocess
filename = "D:\\POO\\Py_work\\arg_parse_file.txt"
'''def add():
    temp = 'mahunta'
    for item in sys.argv[1:]:
        temp = temp+item
        print temp'''

class Super:
    
    def add1(self,a,b,c):
        self.a = int(a)
        self.b = int(b)
        self.c = int(c)
        temp = self.a+self.b+self.c
        return temp


    def initialize(self):
        with open(filename,'r') as self.read_file:
            self.content = self.read_file.readlines()
            print self.content
            

    

