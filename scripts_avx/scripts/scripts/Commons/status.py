#!../../Python/bin/python
import subprocess
import os
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
script_location = os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))

class status:
    def __init__(self):
        pass

    def getStatus(self, user_input):
        cmd = "cd " + script_location + "; ./appviewx --status " +\
            " ".join(user_input)
        # print (cmd)
        out = self.runCommand(cmd)
        # print (out)
        if "not running" in str(out):
            return "False"
        else:
            return "True"

    @staticmethod
    def runCommand(cmd):
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        out = p.stdout.decode()
        return out.lower()
"""
if __name__ == "__main__":
    s = status()
    print (s.getStatus("mongodb"))
"""
