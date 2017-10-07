from fabric.api import run,env

env.hosts = ['localhost']


def host_type():
    run("uname -a")
