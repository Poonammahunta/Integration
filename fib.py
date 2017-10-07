#Write a Python program to get the factorial of a non-negative integer.  
#Write a Python program to solve the Fibonacci sequence using recursion 
#number = 3 [0,1,2]

'''def fact(number):
    product = 1
    if number >0:
        for i in range(number,0,-1):
            product = product*i    

        return product
    if number == 0:
        return "1"


number = int(raw_input("Enter the value: "))
prod = fact(number)
print prod'''

#number =4

def rec(number):
    if number == 0:
        return 1
    else:
        number = number*rec(number-1)
        return number


print rec(5)
        
        
                        
            
        
