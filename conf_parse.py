#!/ usr/bin/pthon


import os, sys, ConfigParser

conf = ConfigParser.ConfigParser()
conf.read("conf_parse_test.ini")

for section_name in conf.sections():
    print "Sections: ", section_name
    print "Options: ", conf.options(section_name)
    for name ,value in conf.items(section_name):
        print "%s = %s",(name,value)

