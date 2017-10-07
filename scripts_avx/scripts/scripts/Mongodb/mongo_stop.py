import os
import sys
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
import set_path
import socket
import subprocess
import logger
avx_path = set_path.AVXComponentPathSetting()
hostname = socket.gethostbyname(socket.gethostname())
lggr = logger.avx_logger('MONGODB')
avx_path = set_path.AVXComponentPathSetting()
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

def mongo_stop():
    try:
        lggr.debug('Stoping mongodb in %s' % (hostname))
        cmd = avx_path.appviewx_path + 'db/mongodb/bin/mongod --dbpath ' + \
            avx_path.appviewx_path + 'db/mongodb/data/db --shutdown'
        lock_file = avx_path.appviewx_path + '/db/mongodb/data/db/mongod.lock'
        if os.path.exists(lock_file):
            with open(lock_file) as fd:
                process_id = fd.readlines()
        process_id = process_id[0].strip('\n')
        kill_cmd = 'kill -9 ' + process_id
        lggr.debug('Shutdown mongodb operation : %s' % process_id)
        ps = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        ps.stdout.close()
        lggr.debug('Killing DB process_id : %s' % process_id)
        ps = subprocess.Popen(
            kill_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        ps.stdout.close()
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        sys.exit(1)
    except Exception as e:
        print(e)
        print("Error in stopping service in %s" % hostname)
if __name__ == '__main__':
    mongo_stop()
