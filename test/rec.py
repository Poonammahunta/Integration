#1.Write a Python program (recursion function) to
#calculate the sum of a list of numbers. 
#target = 5(0-4)

def rec(temp):
    target = int(raw_input("Enter the number for addition: "))
    
    if target != 0:
        for i in range(target,0,-1):
            temp = temp*i
        return temp
        
    else:
        temp = "0"
        return temp



result = rec(temp= 1)
print result


    
