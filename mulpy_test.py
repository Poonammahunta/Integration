import os
import sys
sys.path.append("D:\\POO\\Py_work")


def mount_details():
    """
    Prints the mount details
    """
    result = []
    if os.path.exists('arg_parse_file.txt'):
        fd = open('arg_parse_file.txt')
        for line in fd:
            line = line.strip()
            words = line.split()
            #print('%s on %s type %s' % (words[0],words[1],words[2]))
            if len(words) > 5:
                res = ('(%s)' % ' '.join(words[3:-2]))
            else:
                res = ""
            result.append(res)
        return result    


if __name__ == '__main__':
    s = mount_details()
    for line in s:
        print line[1]

    
