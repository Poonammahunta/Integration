print ("choice 1:Addition")
print ("choice 2:Substraction")
print ("choice 3:Multiplication")
print ("choice 4:Division")

def get_float(prompt):
    while True:
        try:
            return float(raw_input(prompt))
        except:
            print "Invalid Input"
            

choice = int(raw_input("Enter your choice: "))

while True:
    con = float(raw_input("Enter the first number: "))
    if choice == 1:
        i = get_int("Enter the second number: ")
        con = con+i
        print con
        cho = int(raw_input("Enter your choice: "))

    if choice == 2:
        while True:
            i = get_int("Enter the second number: ")
            con = con-i
            print con
            cho = int(raw_input("Enter your choice: "))
    if choice == 3:
        while True:
            i = get_int("Enter the second number: ")
            con = con*i
            print con
            cho = int(raw_input("Enter your choice: "))

    if choice == 4:
        while True:
            i = get_int("Enter the second number: ")
            con = con/i
            print con
            cho = int(raw_input("Enter your choice: "))
            
            
