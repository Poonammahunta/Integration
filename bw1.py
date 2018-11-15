def sub(temp,i,j):
    temp = 0
    i = int(raw_input("Enter the first input: "))
    temp = i - temp
    while True:
        j = int(raw_input("Enter the second input: "))
        temp = temp-j
        return temp

def add(temp,i,j):
    i = int(raw_input("Enter the first input: "))
    j = int(raw_input("Enter the second input: "))
    temp = i+j
    return temp
    
        

result1 = sub(temp,i,j)
print result1
result2 = add(temp,i,j)
print result2
