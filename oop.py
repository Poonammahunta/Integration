'''d = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
l = d.values()
new_d = {}
new_l = []

def asce():
    while l:
        tmp = l[0]
        for item in l:
            if item >= tmp:
                tmp = item
            else:
                pass    
        new_l.append(tmp)
        l.remove(tmp)
        
    for item in range(len(new_l)):
        new_d[d.keys()[item]] = new_l[item]
    print new_d

d1 = {}
s = raw_input("Enter a number: " )
def gen():
    for item in range(1,int(s)+1):
        d1[item] = item*item

    print d1'''
d = {'key1': 1, 'key2': 3, 'key3': 2}
d1 = {'key1': 1, 'key2': 2}
l = []
def sum_val():
    for k,v in d.items():
        for k1,v1 in d1.items():
            if k == k1 and v == v1:
                l.append({k,d[k]})
            else:
                pass
    print l        

if __name__ == "__main__":
    #asce()
    #gen()
    sum_val()
         
            



