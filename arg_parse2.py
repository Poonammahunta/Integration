# p1.py
import sys
sys.path.append('..')
import subprocess
import arg_parse1
filename = "D:\\POO\\Py_work\\arg_parse_file.txt"
new_list = []

def initialize(filename):
    with open(filename,'r') as read_file:
        content= read_file.readlines()
        
        #arg_parse1.add(['first car', 'love with', 'red flower'])
        for item in content:
            item = item.split('\n')[0]
            new_list.append(item)
            print new_list
        arg_parse1.add(new_list)    
        


            

if __name__ == "__main__":
    initialize(filename)
            

    
