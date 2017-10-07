import os
import sys
import socket
import subprocess
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
import set_path
import avx_commons
import logger
lggr = logger.avx_logger('GATEWAY')
avx_path = set_path.AVXComponentPathSetting()
hostname = socket.gethostbyname(socket.gethostname())
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)


def gateway_stop(port):
    try:
        lggr.debug('Port running for gateway : ' + port)
        process_id = "ps x | grep avxgw | awk '{print $1}'"
        lggr.debug('Killing process id : [%s] running for gateway : ' % process_id)
        kill_proc = avx_commons.kill_process(process_id)
    except Exception:
        print("Error in stopping gateway for %s" % hostname)

if __name__ == '__main__':
    gateway_stop(sys.argv[1])
