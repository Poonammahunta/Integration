target = int(raw_input("Enter the value: "))
roman = ''
def rom(target,d,roman):
    temp = d.keys()
    for i in range(len(temp)):
        if target > temp[i]:
            continue
        if target == temp[i]:
            roman = roman+str(d[temp[i]])
            target = target - temp[i]
            return roman, target
        else:
            target = target - temp[i-1] 
            roman = roman+str(d[temp[i-1]])
        return roman,target
        
d = {
    1:'i',
    4:'iv',
    5:'v',
    9:'ix',
    10:'x',
    40:'xl',
    50:'l',
    90:'xc',
    100:'c',
    400:'cd',
    500:'d',
    900:'cm',
    1000:'m'
    }

while target > 0:
    roman,target = rom(target,d,roman)
print roman,target




    
    
    
    
            

        
    


    
    
    

    
    
        
    
        
        


            
        
        
        
    
        
