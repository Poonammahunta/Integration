import os
import sys
var = raw_input("Enter the directory to search for : ")
current_dir = os.path.realpath(os.path.dirname(__file__))
#print current_dir
#os.path.join(current_dir,var)
list_duplicate = list()

if not os.path.isdir(os.path.join(current_dir,var)):
    print "Not Exist!!!"
else:
    for root,dirs,files in os.walk(os.path.join(current_dir,var)):
        s = [files if files.endswith('.pdf')]
        list_duplicate.append(s)        
    #print list_duplicate
