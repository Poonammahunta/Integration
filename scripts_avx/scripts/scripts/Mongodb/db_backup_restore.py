#!../Python/bin/python
##**************************************************************
##
## Copyright (C), AppViewX, Payoda Technologies
##
## Main appviewx script which will call other scripts for various operations
## to start,stop,restart,repair,license renewall,etc.
##
## This script should be placed in 'script' folder of AppViewX
##
## V 1.0 / 21 January 2015 / Murad / murad.p@payoda.com
##
##
##**************************************************************

import os
from avx_commons import run_local_cmd
try:
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    egg_cache_dir = os.path.join(current_file_path+'/.python_egg_cache')
    if not os.path.exists(egg_cache_dir):
        os.makedirs(egg_cache_dir)
    run_local_cmd('chmod g-wx,o-wx ' + egg_cache_dir)
    os.environ['PYTHON_EGG_CACHE'] = egg_cache_dir
except Exception:
    pass
import datetime
import subprocess
import sys
import glob
import os
from termcolor import colored
env_path=os.path.dirname(os.path.realpath(__file__)) + '/'
if not os.path.realpath(env_path + '/../Commons/') in sys.path:
    sys.path.append(os.path.realpath(env_path + '/../Commons/'))
import set_path
import socket
from mongodb_setup import print_success
avx_path = set_path.AVXComponentPathSetting()
hostname = socket.gethostbyname(socket.gethostname())
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
import logger
lggr = logger.avx_logger('MONGODB_BACKUP/RESTORE')
from status import status
s = status()

def help_fun():
    """help_fun display text to guide user
        incase of invalid arguments given
        by user or upon request

    """
    print ("""\n    usage: ./appviewx --dbbackup [argument] \n \
    usage: ./appviewx --dbrestore [argument] \n \
   options:\n \
   \t --dbbackup \t \t to take db backup \n \
   \t --dbrestore \t \t to restore db from backup \n \

   [argument]: \n \
     \t <path> \t \t \t db backup path \n \
     \n \

   example: """+colored("""\n \
     \t 1. appviewx --databasebackup /home/appviewx/db_backup \n \
     \t 2. appviewx --databasebackup \n \
     \t 3. appviewx --databaserestore /home/appviewx/db_backup \n \
     \t ""","red"))

    return True

def check_file_size():
    import psutil
    space = psutil.disk_usage(current_file_path + '/../../../')
    free_space = space.free >> 20
    if not os.path.exists(current_file_path + '/../../db/mongodb/data/'):
        lggr.error('Data directory not Found')
        print('Data directory not Found')
        sys.exit()
    cmd = 'du -s ' + current_file_path + '/../../db/mongodb/data/'
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data_size = int(int(ps.communicate()[0].decode().split('\t')[0]) / 1024)
    if (data_size/30 > free_space):
        lggr.error('Free Space is less than the expected backup file Size. Clear disk space')
        print('Free Space is less than the expected backup file Size. Clear disk space')
        sys.exit(1)

def dbbackup(user_input, conf_data):
    """dbbackup is the main function of appviewx --dbbackup.
        it takes mongodb backup

    """
    try:
        lggr.debug('Checking the file size before initiating the backup operation')
        lggr.info('Checking the file size before initiating the backup operation')
        check_file_size()
        lggr.debug('Executing db backup operation')
        lggr.info('Executing db backup operation')
        lggr.debug('User_input for mongo backup :%s ' % user_input)
        lggr.info('User_input for mongo backup :%s' % user_input)
        appviewx_dir = avx_path.appviewx_path
        if len(user_input) == 0:
            db_backup_dir = appviewx_dir + 'db_backup'
        elif os.path.isabs(os.path.abspath(user_input[0])):
            db_backup_dir = os.path.abspath(user_input[0])
        else:
            print (colored('\n Wrong input - db backup directory path ','red'))
            sys.exit(1)
        backup_type = 'Advanced'
        
        if len(user_input) > 1 and user_input[1].lower() == 'basic':
            backup_type='Basic'
            basic_dbs = ['appviewx','aggregatedStat','configDB','quartz','imageDetails','statistics','templateDB','workFlowDB','workFlowDBEngine']
        
        db_backup_sub_dir = 'db_'+str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        if os.path.exists(db_backup_dir):
             if not os.access(db_backup_dir, os.W_OK):
               print (colored('\nWrite access denied for the %s directory' % user_input[0],'red'))
               sys.exit(1)
        else:
             if not os.access(os.path.dirname(db_backup_dir), os.W_OK):
               print (colored('\nWrite access denied for the %s directory' % user_input[0],'red'))
               sys.exit(1)
        db_backup_dir = db_backup_dir + "/" +db_backup_sub_dir
        lggr.debug('Directory for db backup : %s' % db_backup_dir)
        if not os.path.exists(db_backup_dir):
            os.makedirs(db_backup_dir)
        from avx_commons import get_db_details,get_mongo_username_path
        db_details, instance = get_db_details(conf_data)
        from avx_commons import db_connect
        db_host = db_connect(db_details, instance)
        inputs = ['mongodb',db_host.split(':')[0]]
        if not s.getStatus(inputs) == "True":
           print (colored('DB is not running','red'))
           sys.exit(1)
        from avx_commons import get_db_credentials
        db_username, db_password, db_name = get_db_credentials()
        print_success('Database Backup', 'Started')
        try:
                lggr.debug('Getting username and path for mongodb user')
                username, user_path = get_mongo_username_path(
                    conf_data, hostname)
                lggr.debug('Mongodb username : %s and path : %s' % (username, user_path))
        except Exception:
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
                sys.exit(1)
        if backup_type.lower() == 'advanced':
           cmd = appviewx_dir + \
                '/db/mongodb/bin/mongodump --host ' +\
                str(db_host) + ' --username '+db_username+' --password '+db_password+' --authenticationDatabase '+db_name+' --out ' + db_backup_dir
        else:
           for db in basic_dbs:
                cmd = appviewx_dir + \
                      '/db/mongodb/bin/mongodump --host ' +\
                      str(db_host) + ' --username '+db_username+' --password '+db_password+' --authenticationDatabase '+db_name+ ' --db ' + db + ' --out ' + db_backup_dir  
        lggr.debug('Command for db_backup : %s' % (cmd.replace('-p ' + db_password, '-p ********')))
        lggr.info('Command for db_backup : %s' % (cmd.replace('-p ' + db_password, '-p ********')))
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        _ = ps.communicate()[0]
        ps.stdout.close() 
        print_success('Database Backup', 'Finished')
        parent_directory = str(os.path.abspath(os.path.join(db_backup_dir, os.pardir)))
        os.chdir(db_backup_dir+'/../')
        cmd = 'tar -cvf '+ db_backup_sub_dir + '.tar.gz ' + db_backup_sub_dir + ">/dev/null 2>&1"
        lggr.debug('Arvhiving db_backup directory : ' + db_backup_dir)
        lggr.debug('Command for Archiving db_backup : %s' % (cmd))
        lggr.info('Command for Archiving db_backup : %s' % (cmd))
        run_local_cmd(cmd)
        print_success('Database Backup', 'Compressed')
        lggr.debug("Mongodb backup directory compressed")
        lggr.info("Mongodb backup directory compressed")
        cmd = 'rm -rf ' + db_backup_sub_dir + " >/dev/null 2>&1"
        lggr.debug('Removing db_backup directory : ' + db_backup_dir)
        lggr.debug('Command for removing db_backup direcory : %s' % (cmd))
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        lggr.debug("Mongodb backup directory removed")
        lggr.info("Mongodb backup directory compressed")
        if len(user_input)>1 and len(glob.glob(os.path.dirname(db_backup_dir) + '/db_*.tar.gz')) > int(user_input[1]):
           lggr.debug("Removing old db backup directories other than new %s backups" % user_input[1])
           lggr.info("Removing old db backup directories other than new %s backups" % user_input[1])
           lggr.debug('The count of db backup directory ' + str(len(glob.glob(os.path.dirname(db_backup_dir) + '/db_*.tar.gz'))))
           files = glob.glob(appviewx_dir + '/db_backup/db_*.tar.gz')
           files.sort(reverse=True)
           for index in range(int(user_input[1]),len(files)):
               lggr.debug('Removing old db_backup directory: %s' % files[index] )
               os.remove(files[index])
           lggr.debug("old db backup directories other than new %s backups has removed" % user_input[1])
           lggr.info("old db backup directories other than new %s backups has removed" % user_input[1])

        return True
    except Exception as e:
        lggr.error('Error in Db backup. : %s' % e)
        sys.exit(1)


def dbrestore(user_input, conf_data):
    """dbbackup is the main function of appviewx --dbbackup.
        it takes mongodb backup

    """
    try:
        lggr.debug('user_input for mongo operation :%s' % user_input)
        appviewx_dir = avx_path.appviewx_path
        if len(user_input) == 0:
            print (colored('\n Wrong input - Expecting backup directory path ','red'))
            sys.exit(1)
        elif not os.path.exists(user_input[0]):
            print (colored('\n Wrong Backup Directory - Expecting correct backup directory path ','red'))
            sys.exit(1)
        else:
            if os.path.isfile(user_input[0]):
               print (colored('\n Wrong Backup Directory - Expecting correct backup directory path.','red'))
               sys.exit(1)
            db_backup_dir = str(user_input[0])+'/'
        lggr.debug('Directory for mongo restore ' + db_backup_dir)
        from avx_commons import get_db_details,get_mongo_username_path
        db_details, instance = get_db_details(conf_data)
        from avx_commons import db_connect
        db_host = db_connect(db_details, instance)
        inputs = ['mongodb',db_host.split(':')[0]]
        if not s.getStatus(inputs) == "True":
           print (colored('DB is not running','red'))
           sys.exit(1)
        from avx_commons import get_db_credentials
        db_username, db_password, db_name = get_db_credentials()
        from avx_commons import db_connection
        try:
                lggr.debug('Getting username and path for mongodb user')
                username, user_path = get_mongo_username_path(
                    conf_data, hostname)
                lggr.debug('Mongodb username : %s and path : %s' % (username, user_path))
        except Exception:
                print(
                    colored(
                        "Error in getting username and path for %s" %
                        ip, "red"))
                sys.exit(1)
        try:
           lggr.debug('Establishing db connection')
           conn = db_connection(conf_data,True)
        except Exception as e:
           print (e)
           print (colored("Couldnt connect to primary db ","red"))
           sys.exit(1)
        cmd = appviewx_dir +\
            '/db/mongodb/bin/mongorestore --host ' +\
            str(db_host) + ' --username '+db_username+' --password '+db_password+' --authenticationDatabase '+db_name+ ' --batchSize=10 --drop ' + db_backup_dir 
        print_success('Database Restore', 'Started')
        lggr.debug(cmd.replace('-p ' + db_password, '-p ********'))
        try:
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0].decode("utf-8")
            if 'failed' in output.lower() or 'error' in output.lower():
               with  open('dbrestore.log','w') as fd:
                     fd.write(output)
               raise Exception
            ps.stdout.close()
        except Exception as e:
            lggr.error('Error in Db restore..For more info...look at the dbrestore.log in the current directory')
            print (colored(\
                '\nFailed in restoring db from ' + db_backup_dir + ' !! ' \
                ,"red"))
            print (colored('For more info...look at the dbrestore.log in the current directory','red'))
            sys.exit(1)
        print_success('Database Restore', 'Completed')
        lggr.info('DB Restore  has been completed')
        lggr.debug('DB Restore  has been completed')
        return True
    except Exception as e:
        sys.exit(1)
