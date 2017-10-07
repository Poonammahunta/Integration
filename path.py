import os
d = {}
l = []
new_d = {}
def oo():
    
    for root,dirs,files in os.walk("D:\POO\Py_work"):
        for filename in [name for name in files if name.endswith(".py")]:
            print filename
            '''temp = os.path.getsize(filename)
            if temp not in d.keys():
                d[temp] = filename
            else:
                l.append((d[temp],filename))'''


    return l            

                
print oo()
