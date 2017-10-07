import os
import paramiko

def exec_cmd(ssh_object,cmd):
    try:
        _,stdout,_ = ssh_object.exec_command(cmd)
        res = stdout.read()
        return res
    except Exception as e:
        print str(e)

def main():
    try:
        cmd = 'cat ~/.ssh/known_hosts'
        get_key_value = exec_cmd(ssh_object,cmd)
        print get_key_value
    except Exception as e:
        print str(e)
