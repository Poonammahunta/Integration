#!../../Python/bin/python
##**************************************************************
##
## Copyright (C), AppViewX, Payoda Technologies
##
## This script has to placed inside scripts folder
## This script should be placed in 'script' folder of AppViewX
## Cron sample
## 0 0-6,17-23 * * *  <appviewx_path>/scripts/device_inprogress_status.py
## V 1.0 / 02 June 2015 / Prabakaran.K / prabakaran.k@payoda.com
##
##**************************************************************

#import modules from AppViewX Python
import os
try:
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    egg_cache_dir = os.path.join(current_file_path+'/.python_egg_cache')
    if not os.path.exists(egg_cache_dir):
        os.makedirs(egg_cache_dir)
    os.system('chmod g-wx,o-wx ' + egg_cache_dir)
    os.environ['PYTHON_EGG_CACHE'] = egg_cache_dir
except Exception:
    pass
#import httplib2
#import urllib2
import ast
from configobj import ConfigObj
import sys
import socket
import time
import traceback
#AppViewX conf file localtion
current_location = os.path.dirname(os.path.realpath(__file__))
conf_file_path = (str(current_location)+'/../../conf/appviewx.conf')
from avx_commons import db_connection,get_db_credentials

# Below package are for smtp library
import smtplib
import sys

#Read properties from conf file
try:
  conf_data = ConfigObj(conf_file_path)
except Exception as e:
  print (' conf file ERROR!! ')
  sys.exit(1)

def smtp_configuration(device_id,device_fid,device_uid,device_umid):
        '''
        Function helps to configure the smtp for the particular server
        '''
        sender = 'muthuramalingam.p@mail.appviewx.in'
        receivers = 'muthuramalingam.p@mail.appviewx.in'
        smtp_server_name = '192.168.' + '96.112'
        smtp_server_port = '25'
        message = """From:""" + sender + """
To:""" + receivers + """
MIME-Version: 1.0
Content-type: text/html
Subject: AppViewX Device Inventory Status Notification

<b>
  <p> <span style='font-size:20px;'><strong>App<span style='color:#008000;'>ViewX</span> Notification</strong></span></p>
  <hr />
  <ul>
         """ "Devices that are in In-Progress status : " + device_id  +  """ <br>
         """ "Devices that are in Failed status : " + device_fid  +  """ <br>
         """ "Devices that are in Unresolved statues : " + device_uid + """ <br>
         """ "Devices that are in Unmanaged statues : " + device_umid + """ <br>
         <li> <span style='font-size:14px;'><strong>Solution:&nbsp;</strong>Try to restart the respective components or please contact support team&nbsp;</span></li>
  </ul>
  <hr />
  <p> <span style='font-size:12px;'>Please do not reply as this is an auto generated email by AVX.</span></p>
</b>
"""
        return sender,receivers,smtp_server_name,smtp_server_port,message


'''
To check appviewx version from conf file
'''

def decrypt_password(password):
    cmd = str(current_location)+'/../jre/bin/java -jar '+str(current_location)+'/../properties/appviewx_encrypt_util.jar d '+SERVICE_PASSWORD
    import subprocess
    try:
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        password=ps.communicate()[0]
        return password
    except Exception:
        print (str(e))


'''
AppViewX DB connection based on the version
'''
def db_connection(version_check):        
        from pymongo import MongoClient,ReadPreference
        if conf_data['ENVIRONMENT']['MULTINODE'].lower()=='false':
            mongo_ip=conf_data['MONGODB']['HOSTS'][0]
        else:
            db =''
            mongo_ip=conf_data['MONGODB']['HOSTS']
            try:
                conn = MongoClient(mongo_ip)
                username,password,dbname = get_db_credentials()
                conn.admin.authenticate(username,password,source=dbname)
                db=conn.appviewx
            except Exception:
                pass
        if db =='':
           print ('Couldnt connect to DB')
           sys.exit(1)
        return db


'''
To trigger config fetch for the inprogress devices
'''
def trigger_config_fetch(db):
    inprogress_devices=db.device.find({"status":{"$regex":"Inprogress"}})
    failed_devices=db.device.find({"status":{"$regex":"Failed"}})
    unresolved_devices=db.device.find({"status":{"$regex":"Unresolved"}})
    unmanaged_devices=db.device.find({"status":{"$regex":"Unmanaged"}})
    count =0
    device_id=""
    for device in inprogress_devices :
        device_id = device_id + device['name'] + ","
    device_id=device_id.strip(',')
    device_fid=""
    for fdevice in failed_devices :
        device_fid = device_fid + fdevice['name'] + ","
    device_fid = device_fid.strip(',')
    device_uid=""
    for udevice in unresolved_devices :
        device_uid = device_uid + udevice['name'] + ","
    device_uid = device_uid.strip(',')
    device_umid=""
    for umdevice in unmanaged_devices :
        device_umid = deivce_umid + umdevice['name'] + ","
    device_umid = device_umid.strip(',')
    return device_id,device_fid,device_uid,device_umid
        
if __name__ == '__main__':
    version_check=conf_data['COMMONS']['VERSION']
    db=db_connection(version_check)
    device_id,device_fid,device_uid,device_umid=trigger_config_fetch(db)
    if device_id or device_fid or device_uid or device_umid:
        if device_id:
           print ("List of devices that are in In-Progress :" + str(device_id))
        if device_fid:
           print ("List of devices that are in Failed :" + str(device_fid))
        if device_uid:
           print ("List of devices that are in Unresolved :" + str(device_uid))
        if device_umid:
           print ("List of devices that are in Unmanaged :" + str(device_umid))
        sender,receivers,smtp_server_name,smtp_server_port,message = smtp_configuration(device_id,device_fid,device_uid,device_umid)
        smtpObj = smtplib.SMTP(smtp_server_name,smtp_server_port)
        smtpObj.sendmail(sender, receivers, message)
        print ("sucesssfully triggred the mail")
    else:
      print ("No devices has been added in the inventory list")



