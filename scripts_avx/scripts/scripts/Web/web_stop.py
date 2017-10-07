import os
import sys
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
import set_path
import avx_commons
import socket
import subprocess
avx_path = set_path.AVXComponentPathSetting()
hostname = socket.gethostbyname(socket.gethostname())
import logger
lggr = logger.avx_logger('WEB')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
def web_stop(port):
    try:
        cmd = avx_path.web_apache_path + "bin/shutdown.sh"
        lggr.debug('Web running on port:%s' % port)
        lggr.debug('Command to stop web :%s' % cmd)
        ps=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        ps.stdout.close()
        process_id = 'lsof -t -i:' + port
        kill_proc = avx_commons.kill_process(process_id)
    except Exception as e:
        print (e)
        print("Error in stopping service in %s" % hostname)
if __name__ == '__main__':
    web_stop(sys.argv[1])
