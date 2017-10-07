# Roman to decial conversion

t = raw_input("Enter the roman value: ")
total = 0
d = {'i':1,
     'v':5,
     'x':10,
     'l':50,
     'c':100,
     'd':500,
     'm':1000}
def dec(total,d,t):
    if len(t) == 1:
        return d[t[0]]
    
    for i in range(len(t)-1):
        if d[t[i]] >= d[t[i+1]]:
            total = total+d[t[i]]
        if d[t[i]] < d[t[i+1]]:
            total = total -d[t[i]]
        else:
            total = total+d[t[-1]]
            
    return total



tot = dec(total,d,t)
print tot


    



    
    
