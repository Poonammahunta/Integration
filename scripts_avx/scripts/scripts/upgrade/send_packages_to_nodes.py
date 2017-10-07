import os 
import sys
currentframe = os.path.dirname(os.path.realpath(__file__))
if not os.path.realpath('Commons/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Commons/'))
if not os.path.realpath('Mongodb/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Mongodb/'))
if not os.path.realpath('Web/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Web/'))
if not os.path.realpath('Gateway/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Gateway/'))
if not os.path.realpath('Plugins/') in sys.path:
   sys.path.append(os.path.realpath(currentframe + '/../Plugins/'))
file_location = sys.argv[1]
from avx_commons import run_local_cmd
# if os.path.exists(file_location):
from config_parser import config_parser
conf_data = config_parser(currentframe + '/../../conf/appviewx.conf')
from pprint import pprint
pprint(conf_data)


