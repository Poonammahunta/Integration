import os
import sys
import socket
import subprocess
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
import set_path
import avx_commons
import logger
lggr = logger.avx_logger('LOGSTASH')
avx_path = set_path.AVXComponentPathSetting()
hostname = socket.gethostbyname(socket.gethostname())
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def logstash_stop(port):
    try:
        lggr.debug('Port running for logstash : ' + port)
        cmd  = "(ps -eaf | grep " + avx_path.appviewx_path + "/logstash | grep -v grep | awk '{ print $2}')"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
        out, err = p.communicate()
        process_id = out.decode('utf-8')
        kill_cmd = 'kill -9 ' + process_id
        lggr.debug('Killing process id : [%s] running for logstash : ' % process_id)
        p = subprocess.Popen(kill_cmd, stdout=subprocess.PIPE,shell=True)
    except Exception:
        print("Error in stopping logstash for %s" % hostname)

if __name__ == '__main__':
    logstash_stop(sys.argv[1])
