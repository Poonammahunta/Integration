#import pdb;pdb.set_trace()

'''def combine(s1,s2):      # define subroutine combine, which...
    s3 = s1 + s2 + s1    # sandwiches s2 between copies of s1, ...
    s3 = '"' + s3 +'"'   # encloses it in double quotes,...
    return s3            # and returns it.

a = "aaa"
pdb.set_trace()
b = "bbb"
c = "ccc"
final = combine(a,b)
print final'''


f = "D:\\POO\\Py_work\\test\\old.txt"

with open(f) as open_file:
    content = open_file.readlines()
    for line in content:
         import pdb;pdb.set_trace()
         if "string" in line:
             print line[line.index("string")]
