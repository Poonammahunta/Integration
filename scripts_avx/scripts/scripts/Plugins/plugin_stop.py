import os
import sys
if not os.path.dirname(__file__) + '/../Commons' in sys.path:
    sys.path.insert(0, os.path.dirname(__file__) + '/../Commons')
import avx_commons
import set_path
import socket
import subprocess
avx_path = set_path.AVXComponentPathSetting()
import logger
lggr = logger.avx_logger('PLUGINS')
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

def plugin_stop(jar_file, port):
    lggr.debug('%s running on port :%s' % (jar_file.split('.jar'),port))
    process_id_cmd = 'netstat -tupln | grep ' + port
    process_id = subprocess.run(process_id_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
    lggr.debug('Killing process_id : %s' % process_id)

    try:
        pid = process_id.strip().split()[-1].split('/')[0]
        kill_cmd = 'kill -9 ' + pid
        subprocess.run(kill_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except IndexError:
        lggr.debug('No process running on port ' + port)
        return


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print("Error in user input")
    plugin_stop(sys.argv[1], sys.argv[2])
