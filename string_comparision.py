#a = "123456"
#b = "987645"
#c = "abdcef"




'''if len(a) != len(b):
    print "False"
else:
    count = 0
    while count < len(a):
        if a[count] != b[count]:
            print a[count],b[count]
            print "False"
            break
        count = count+1
    else:
        print "True"'''


'''if len(a) != len(b):
    print "False"

else:
    count = 0
    while count < len(a1):
        print a1[count]
        
        if a1[count] in b1:
            print a1[count]
            break
        count = count+1
    else:
        print "True"'''

a = "t-abdae"
b = "t-abcde"
c = "t-abcdef"
a1 = list(a)
b1 = list(b)

'''if len(a) != len(b):
    print "False"
else:    
    count = 0
    while count < len(a1):
        if a1[count] in b1:
            print a1[count]
        else:
            print "false"
            break
        count = count+1
        
    else:
        print "True"

1. take a empty dictionary
2. fill the dict with elements of a. value = count
3. traverse b and check elements and occurance with dict....if ok result = true
4. traverse c and check elements and occurance with dict....'''

a = "t-abdae"
b = "t-abcde"
c = "t-abcdef"
a1 = list(a)
b1 = list(b)

def create_dict():
    
    d = {}
    count = 1
    for i in a1:
        if i not in d:
            d[i] = count
        else:
            d[i] = count+1
    return d

def compare():
    s = create_dict()
    count =1 
    for i in b1:
        if i in b1:
            
        
        
            
            
    
        
        
        
    
            

        
            
