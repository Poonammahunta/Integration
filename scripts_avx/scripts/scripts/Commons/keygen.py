"""Keygen."""
import getpass
import re
import sys
try:
    import paramiko
except ImportError:
    print ("Python Paramiko pacakge is not available hence ssh keys cannot be passed")
    sys.exit(1)
ssh_node = paramiko.SSHClient()
ssh_node.set_missing_host_key_policy(paramiko.AutoAddPolicy())
copy_key_node_object = paramiko.SSHClient()
copy_key_node_object.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# -----------------------------------------------------------------------
# Node Details should be a comma separated list of IPs
# -----------------------------------------------------------------------
node_details = ['<IP1>', '<IP2>']
# -----------------------------------------------------------------------
# User details should be a comma separated list of users of the nodes
# -----------------------------------------------------------------------
user_details = ['appviewx', 'appviewx']
# -----------------------------------------------------------------------
# Port details should be a comma separated list of integer SSH ports of above nodes
# -----------------------------------------------------------------------
port_details = [22, 22]
# -----------------------------------------------------------------------


class Bcolors:
    """."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def ipv4_validation(node_details):
    """."""
    for ip in node_details:
        if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip):
            return True
        else:
            print (Bcolors.FAIL + '\n ERROR!! Invalid IP (IPv4) format: %s\n' % ip + Bcolors.ENDC)
            sys.exit(1)


def getpassword(usernames, node_details):
    """Function to get passwords of nodes."""
    try:
        # node_password - list to get password of nodes
        node_password = list()
        username_node = list(zip(usernames, node_details))
        for i in range(len(node_details)):
            password = getpass.getpass("password for %s@%s : " % (username_node[i][0], username_node[i][1]))
            node_password.append(password)
        return node_password
    except Exception as e:
        print (e)
        sys.exit(1)


def connect_node(ip, username, passwrd=None, port=22, look_for_keys=True):
    """The function to create SSH object for all nodes."""
    try:
        ssh_node.connect(ip, username=username, password=passwrd, port=port, look_for_keys=look_for_keys, timeout=10)
        return ssh_node
    except paramiko.AuthenticationException:
        print (Bcolors.FAIL + '\n Authentication failed when connecting to %s \n' % ip + Bcolors.ENDC)
        sys.exit(1)
    except Exception as e:
        print (Bcolors.FAIL + '\n ERROR: Could not reach %s (%s)\n' % (ip, e) + Bcolors.ENDC)
        sys.exit(1)


def extract_python():
    """Function to extract python from the AppViewX package."""
    import os
    import subprocess
    while True:
        package_path = os.path.abspath(input('Enter the path of AppViewX installer package.'))
        if os.path.isfile(package_path) and package_path.endswith('.tar.gz') and 'license' not in package_path.lower():
            break
    cmd_to_extract = 'tar -xf ' + package_path + ' Python/'
    subprocess.run(cmd_to_extract)


def getkeygen(username_node_passwd):
    """Check for public key."""
    """getkeygen will visit each node to check for public key.
    If public key does not exist, it will create public key and copy to all other nodes'
    authorized keys.

    """

    try:
        for node in username_node_passwd:
            ssh_object = connect_node(node[1], node[0], node[2], node[3])
            cmd = " if [ -f ~/.ssh/id_rsa.pub ]; then echo 'pub_key_exist'; else echo 'not_exist'; fi ;"
            # check if public key already exist
            try:
                file_exist = exec_cmd(ssh_object, cmd)
            except Exception as e:
                file_exist = 'not_exist'
            if str(file_exist.strip()) == 'not_exist':
                try:
                    cmd = ' mkdir -p ~/.ssh && cd ~/.ssh/ && ssh-keygen -t rsa -f id_rsa -q -N ""'
                    # run above command in remote node
                    exec_cmd(ssh_object, cmd)
                except Exception as e:
                    try:
                        cmd = 'mkdir -p ~/.ssh'
                        exec_cmd(ssh_object, cmd)
                        cmd = ' cd ~/.ssh/ && ssh-keygen -t rsa -f id_rsa -q -N ""'
                        # run above command in remote node
                        exec_cmd(ssh_object, cmd)
                    except Exception as e:
                        print (e)
            cmd = "cat ~/.ssh/id_rsa.pub"
            # get public key value
            get_key_value = exec_cmd(ssh_object, cmd)
            for share_keygen_node in username_node_passwd:
                try:
                    copy_key_node_object.connect(
                        share_keygen_node[1],
                        username=share_keygen_node[0],
                        password=share_keygen_node[2],
                        port=share_keygen_node[3])
                except paramiko.AuthenticationException:
                    print (Bcolors.FAIL + '\n Authentication failed when connecting to %s' % share_keygen_node[1] + Bcolors.ENDC)
                    sys.exit(1)
                except Exception as e:
                    print (e)
                    sys.exit(1)
                if get_key_value.endswith('\n'):
                    get_key_value = get_key_value.strip("\n")
                mkdir_cmd = "mkdir -p ~/.ssh"
                exec_cmd(copy_key_node_object, mkdir_cmd)
                # check if authorized key file already exist
                cmd = " if [ -f ~/.ssh/authorized_keys ]; then echo 'authorized_keys_exist'; else echo 'not_exist'; fi ;"
                try:
                    authorized_keys_exist = exec_cmd(copy_key_node_object, cmd)
                except Exception as e:
                    try:
                        create_cmd = " mkdir -p ~/.ssh"
                        exec_cmd(copy_key_node_object, create_cmd)
                        authorized_keys_exist = exec_cmd(copy_key_node_object, cmd)
                    except Exception as e:
                        print (e)

                if authorized_keys_exist.strip("\n") == 'authorized_keys_exist':
                    cat_authorized_keys = 'cat ~/.ssh/authorized_keys'
                    cat_authorized = exec_cmd(copy_key_node_object, cat_authorized_keys)
                    # check if already key in node
                    if get_key_value not in cat_authorized:
                        # sharing key if authorized_key exist and key not in it
                        place_key_cmd = "echo " + get_key_value + " >> ~/.ssh/authorized_keys"
                        exec_cmd(copy_key_node_object, place_key_cmd)

                else:
                    # creating and sharing key if authorized_key not preasent
                    place_key_cmd = "echo " + get_key_value + " >> ~/.ssh/authorized_keys"
                    exec_cmd(copy_key_node_object, place_key_cmd)
                # changing permission for authorized_keys
                file_permission_cmd = "chmod 640 ~/.ssh/authorized_keys"
                exec_cmd(copy_key_node_object, file_permission_cmd)
                # changing permission for authorized_keys
                ssh_dir_permission_cmd = "chmod 700 ~/.ssh"
                exec_cmd(copy_key_node_object, ssh_dir_permission_cmd)
                copy_key_node_object.close()
            ssh_object.close()
        return True
    except Exception as e:
        print (e)
        sys.exit(1)


def exec_cmd(ssh_object, cmd):
    """Exceute command on a particular node."""
    try:
        # ssh_object - paramiko object
        # cmd - system command(s)
        _, stdout, _ = ssh_object.exec_command(cmd)
        res = stdout.read()
        return res.decode()
    except Exception as e:
        print(e)
        sys.exit(1)


def passkeygen(node_details, usernames, port_details):
    """The function is used to facilitate the key exchange based upon node and user details."""
    try:
        node_password = list()
        usernames = usernames * len(node_details)
        node_password = getpassword(usernames, node_details)
        username_node_passwd = list(zip(usernames, node_details, node_password, port_details))
        getkeygen(username_node_passwd)
        print (Bcolors.OKGREEN + '\n Success. RSA keys are copied to all the servers\n' + Bcolors.ENDC)
        return True
    except Exception as e:
        print (e)
        sys.exit(1)


if __name__ == '__main__':
    user_input = sys.argv
    if len(user_input) not in [1, 4]:
        print('Keygen file takes no arguement')
        sys.exit(1)
    if len(user_input) == 4:
        node_details = user_input[1].split(',')
        user_details = user_input[2].split(',')
        port_details = list(map(int, user_input[3].split(',')))

    try:
        ipv4_validation(node_details)
        passkeygen(node_details, user_details, port_details)
    except KeyboardInterrupt:
        print (Bcolors.FAIL + '\n Keyboard Interrupt\n' + Bcolors.ENDC)
        sys.exit(1)
    except Exception as e:
        sys.exit(1)
