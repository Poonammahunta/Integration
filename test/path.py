'''import os
d = {}
for root,dirs,files in os.walk("D:\POO\Py_work"):
    for filename in [os.path.join(root,name) for name in files if name.endswith(".py")]:
        d[os.path.getsize(filename)] = filename

print d

print os.path.join(os.path.dirname(__file__),'old.txt')'''


def prime_in():
    while True:
        
    
        i = int(raw_input("value: "))
        if i %2 == 0:
            print "this is not prime"
        else:
            print "prime"


s = prime_in()
print s
