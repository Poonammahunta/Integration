'''import datetime
target = raw_input("Enter the date format: ")
s = datetime.datetime.strptime(target,"%Y/%m/%d").strftime("%j")
print s


d = {}
a,b = raw_input("Enter the a,b: ").split(',')
d = {'name': a,'mark': b}
print d

import os

dir_name = os.path.dirname(os.path.abspath(__file__))
s = os.path.dirname(os.path.realpath(__file__))

print dir_name,s'''

import logging
import sys

LEVELS = {'debug':logging.DEBUG,
          'info':logging.INFO,
          'warning':logging.WARNING,
          'error':logging.ERROR,
          'critical':logging.CRITICAL,
          }
if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(level=level)

logging.debug('this is a debug message')
logging.info('this is a info message')
logging.warning('this is a warning message')
logging.error('this is a error message')
logging.critical('this is a critical message')
