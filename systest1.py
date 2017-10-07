import sys
#global tt
def test():
    for item in user_input:
        if 'tt' in item:
            print item.replace('tt','ip1')
            print item
        


if __name__ == "__main__":
    user_input = sys.argv[1:]
    test()
    
