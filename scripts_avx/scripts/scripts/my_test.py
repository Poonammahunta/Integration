def either():
    """."""
    return '[%s%s]' %(c.lower(),c.upper()) if c isalpha() el


class AppViewXTrobuleshot(object):
    """Custom class with fabric module to execute all remote command for AppViewX"""

    def __init__(self,hostname=None,port=22,user=None,pty=True,parallel=False):
        if hostname:
            env.hosts = hostname
        if user:
            env.user = user
        else:
            env.user = 'appviewx'
        self.pty = pty
        env.port = port
        # fabric output would be suppressed
        fabric.state.output['running'] = False
        fabric.state.output['output'] = False
        self.cmd = cmd
        self.parallel = parallel
        if parallel:
            env.parallel = True
        else:
            env.parallel = False

    def _exec_remote_cmd(self):
        """Private function to execute the command with the default settings."""
        """Not to be used by the external system"""
        try:
            with hide('warnings'), settings(warn_only=True, parallel=self.parallel, capture=True):
                if env.hosts[0] == hostname and env.user == getpass.getuser() and len(env.hosts) == 1:
                    result = local(self.cmd, capture=True)
                else:
                    if self.pty:
                        result = run(self.cmd)
                    else:
                        result = run(self.cmd, pty=self.pty)
                return result, result.succeeded
        except Exception:
            raise Exception

    def run(self,cmd,user='appviewx'):
        try:
            cmd = self.cmd
            result = excute(self._exec_remote_cmd)
