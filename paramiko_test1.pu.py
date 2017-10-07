import os
import paramiko

def exec_cmd(ssh_object,cmd):
    try:
        _,stdout,_ = ssh_object.exec_cmd(cmd)
        res = stdout.read()
        return res
    except Exception as e:
        print str(e)



ssh_object = paramiko.SSHClient()
ssh_object.connect('127.0.0.1',username='sanjeeb das',password='engineer@123')
ssh_object.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def main():
    obj = "df -hT"
    out = exec_cmd(ssh_object,obj)
    print out
    
    
if __name__ == "__main__":
    main()
        
