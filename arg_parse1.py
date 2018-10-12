import sys
sys.path.append('..')
#from arg_parse2 import Super



def add(args):
    temp = " "
    for item in args:
        temp = temp+item
    print temp  
    

if __name__ =="__main__":
    import sys
    add(sys.argv[1:])
