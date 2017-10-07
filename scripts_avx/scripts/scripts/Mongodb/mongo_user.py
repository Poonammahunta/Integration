import pwd
import grp
import sys
import os
import socket
import glob
from subprocess import call
import readline
from termcolor import colored
import psutil
import decimal
import subprocess
if os.geteuid() != 0:
   print (colored(
                   "\n \tScript should be execute as root user \n" ,"red"))
   sys.exit(1)

local_ip = socket.gethostbyname(socket.gethostname())
def complete(text, state):
    """."""
    return (glob.glob(text + '*') + [None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

avx_installed_path = input("Enter the appviewx installed path : ")

if not os.path.exists(avx_installed_path + "/conf"):
    print("AppViewX is not installed in the given path: %s " % avx_installed_path)
    sys.exit(1)

if not avx_installed_path + "/scripts/Commons" in sys.path:
    sys.path.append(avx_installed_path + "/scripts/Commons")
from config_parser import config_parser

conf_data = config_parser(str(avx_installed_path) + '/conf/appviewx.conf')


conf_data_keys = conf_data['MONGODB']
key_values = ['MONGO_SEPARATE_USER','MONGO_USER']
missing_value = list()
for key in key_values:
    conf_data['MONGODB'][key.lower()]= [x for x in conf_data['MONGODB'][key.lower()] if x]
    if not (key.lower() in conf_data_keys.keys() and len(conf_data['MONGODB'][key.lower()])):
        missing_value.append(key)
if len(missing_value):
    print("%s field value is missing in conf file" % (missing_value))
    sys.exit(1)
if not local_ip in conf_data['MONGODB']['mongo_ips']:
    print ('Local ip is not configured for separate mongo users')
    sys.exit(1)
if not conf_data['MONGODB']['mongo_separate_user'][0].lower() =='true':
    print ('MONGO_SEPARATE_USER field under MONGODB section is not set as True')
    sys.exit(1)
m_index = conf_data['MONGODB']['mongo_ips'].index(local_ip)
username = conf_data['MONGODB']['mongo_username'][m_index]
path = conf_data['MONGODB']['mongo_path'][m_index]
db_folder = avx_installed_path + '/db'
disk_details = psutil.disk_usage(path)
disk_details = [str(round(decimal.Decimal(
                x / 1024 / 1024 / float(1024)), 1)) for x in disk_details]
destination_file_size = disk_details[2]
cmd = 'du -s ' + db_folder
ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
source_file_size = int(int(ps.communicate()[0].decode().split('\t')[0]) / 1024/ 1024)
if int(round(float(source_file_size))) >=  int(round(float(destination_file_size))):
    print ("Cannot move database data directory(%s) to destination(%s) due to not enough space." % (db_folder,path))
    sys.exit(1)
user_list = list()
for p in pwd.getpwall():
    user_list.append(p[0])
log_path = "mkdir -p " + path + "/logs"
log_file = "touch " +  path + "/logs/db.log"
if username not in user_list:
    l = os.popen('adduser %s' % (username))
    l = os.popen('usermod -s /usr/sbin/nologin %s' % username)
else:
    print("User(%s) already created in the environment" % username)

l = os.popen(log_path)
l = os.popen(log_file)
n_cmd = "su -s /bin/bash " + username + ' -c "ulimit -u"'
u_cmd = "su -s /bin/bash " + username + ' -c "ulimit -n"'
ulimit_n = os.popen(n_cmd).read().strip()
ulimit_u = os.popen(u_cmd).read().strip()
print ("Ulimit(n) : %s" % ulimit_n)
print ("Ulimit(u) : %s" % ulimit_u)
db_folder = avx_installed_path + '/db'
print ('Moving db data from ' + db_folder + ' to ' + path)

args = ["rsync","-avz", db_folder, path]
del_files = ["rm" , db_folder + "/mongodb/data"]
try:
    call(args)
except Exception as e:
    print(e)
    sys.exit(1)
if os.path.exists(avx_installed_path + '/scripts/Commons/.conf_hash.txt'):
   os.remove(avx_installed_path + '/scripts/Commons/.conf_hash.txt')
try:
    l = os.popen('chown %s:%s %s -R' % (username,username,path))
except Exception as e:
    print(e)
    sys.exit(1)
