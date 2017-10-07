#2.Write a Python program of recursion list sum. 
#Test Data : [1, 2, [3,4], [5,6]]
#Expected Result : 21

l= [1, 2, 3,4, 5,6]

def rec(l,temp=0):
    
    for i in l:
        if len(str(i)) == 1:
            temp = temp+i

        else:
            for j in i:
                temp = temp+j
    return temp        
            


result = rec(l)
print result
