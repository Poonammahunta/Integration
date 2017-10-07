'''dic1={1:10, 2:20} 
dic2={3:30, 4:40} 
dic3={5:50,6:60}

new_dic = dict(dic1.items()+dic2.items()+dic3.items())
print new_dic'''

'''dict = {'1': 10, '2': 20, '3': 30, '4': 40, '5': 50, '6': 60}
l = []
def check(dict):
    target = raw_input("Enter the key to check: ")
    for i in dict.keys():
        l.append(i)
    print l    
    if target in l:
        return "key present"
    else:
        return "can add"
    

print check(dict)'''

'''target = int(raw_input("Enter the number: "))
d ={}
for i in range(target):
    d[i+1] = (i+1)*(i+1)
print d'''    

    
