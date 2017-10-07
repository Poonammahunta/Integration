#!../../Python/bin/python
"""File to do apply patch operation during upgrade."""

########################################################################
# #
# # Before running the file, make sure AppViewX is extracted in
# # the following directory:
# #           {old_appviewx_dir}/patch/AppViewX_Patch
# #
# # The license file should be present in the following location:
# #           {old_appviewx_dir}/patch/AppViewX_license.tar.gz
# #
# # The plugins.meta file is present in the following directory:
# #           {old_appviewx_dir}/patch/plugins.meta
# #
########################################################################
import os
import sys
import glob
import socket
import shutil
import logging
import readline
import subprocess
lggr = logging.getLogger('Apply_Patch')
lggr.setLevel(logging.DEBUG)
fh = logging.FileHandler('upgrade.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} ' +
    '%(levelname)s\t%(message)s',
    '%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
lggr.addHandler(fh)
lggr.addHandler(ch)
current_file_location = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostbyname(socket.gethostname())


def complete(text, state):
    """."""
    return (glob.glob(text + '*') + [None])[state]


def either(c):
    """."""
    return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


class ApplyPatch():
    """Class to apply patch."""

    """The following steps are followed while applying patch:
    1. Delete the old directories not needed. These include service and
       iAgent.
    2. Remove old version of JDK, JRE and Python.
    3. Take a backup of scripts, logs ang properties folders.
    4. Copy the new directories."""

    def __init__(self):
        """Class variables."""
        self.patch_path = os.path.abspath(current_file_location + '/../../')
        self.appviewx_path = os.path.abspath(self.patch_path + '/../../')

    def backup_old(self):
        """Take a backup of old scripts, logs and properties directories."""
        import tarfile
        print('Backing up old scripts, logs and properties directories.')
        lggr.debug(
            'Taking a backup of old scripts, logs and properties folders.')
        dirs_to_backup = ['scripts', 'logs', 'properties']
        with tarfile.open(
                os.path.abspath(
                    self.appviewx_path +
                    '/old_scripts_logs_properties.tar.gz'), 'w:gz') as tar:
            for directory in dirs_to_backup:
                try:
                    tar.add(
                        os.path.abspath(self.appviewx_path + '/' + directory))
                except:
                    lggr.debug('Unable to take backup of: ' + directory)
        print('Backup completed successfully.')

    def conf_merge(self, merge=True):
        """Perform conf merge."""
        """Function to take a backup of conf file or perform
        conf merge operation based upon the parameter."""
        if not merge:
            try:
                print('Taking a backup of old appviewx.conf')
                shutil.copyfile(
                    os.path.abspath(self.appviewx_path +
                                    '/conf/appviewx.conf'),
                    os.path.abspath(self.appviewx_path +
                                    '/conf/appviewx_backup.conf'))
                print('appviewx.conf backed up as appviewx_backup.conf.')
            except:
                print('Unable to make appviewx_backup.conf!!')
                lggr.error('Unable to make appviewx_backup.conf!!')
            try:
                loc = os.path.abspath(
                    self.patch_path +
                    '/plugins.meta')
                open(loc, 'r+')
            except:
                while True:
                    loc = os.path.abspath(
                        input(
                            'Enter the location of plugins.meta: '))
                    if os.path.isfile(loc) and loc.endswith(
                            'plugins.meta'):
                        break
            try:
                print('Copying plugins.meta to conf directory.')
                shutil.copyfile(
                    os.path.abspath(loc),
                    os.path.abspath(self.appviewx_path +
                                    '/conf/plugins.meta'))
                print(
                    'Successfully copied plugins.meta' +
                    ' to conf directory.')
            except:
                print(
                    'Unable to copy plugins.meta to conf directory')
        else:
            cmd_for_merge = self.appviewx_path + '/Python/bin/python ' +\
                self.appviewx_path + '/scripts/upgrade/conf_merge.py'
            print('Starting conf merge process')
            ps = subprocess.run(cmd_for_merge, shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            if ps.returncode:
                lggr.error('Unable to perform COnf Merge operation!!')
                print('Unable to perform Conf Merge operation!!')
                lggr.error(
                    'Error ehile doing conf merge: ' + ps.stderr.decode())
            else:
                print('Conf merge completed successfully.')
                lggr.debug('Conf Merge operation completed')

    def remove_old_directories(self):
        """Function to remove old directories."""
        self.dirs_to_remove = ['Plugins', 'avxgw', 'jdk', 'scripts',
                               'jre', 'logs', 'properties', 'Python',
                               'release_scripts', 'service', 'web']
        for directory in os.listdir(self.appviewx_path):
            if directory.startswith('iAgent'):
                self.dirs_to_remove.append(directory)
        print('Cleaning up the installation directory.')

        for directory in self.dirs_to_remove:
            try:
                if os.path.exists(os.path.abspath(
                        self.appviewx_path + '/' + directory)):
                    shutil.rmtree(
                        os.path.abspath(self.appviewx_path + '/' + directory))
                    lggr.debug(
                        'Deleted directory: ' + self.appviewx_path + '/' +
                        directory)
            except:
                lggr.error(
                    'Unable to delete: ' +
                    self.appviewx_path + '/' + directory)
        print('Installation directory cleanup completed.')

    def sync_directories(self):
        """Functio to sync some old directories with new directories."""
        dirs_to_sync = ['db', 'aps', 'conf', 'scripts', 'Python']
        cmd_list = []
        for directory in dirs_to_sync:
            cmd_list.append('rsync -avz ' + os.path.abspath(
                self.patch_path + '/' + directory) + '/ ' +
                os.path.abspath(
                self.appviewx_path + '/' + directory) + '/')

        print('Syncing database...')

        for cmd in cmd_list:
            try:
                ps = subprocess.run(cmd, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            except:
                lggr.error(
                    'Unable to sync: ' + cmd.split('/')[-1] + ' directory!!')
                print(
                    'Unable to sync: ' + cmd.split('/')[-1] + ' directory!!')
                continue
            if ps.returncode:
                lggr.error(
                    'Unable to sync: ' + cmd.split('/')[-1] + ' directory!!')
                print(
                    'Unable to sync: ' + cmd.split('/')[-1] + ' directory!!')
            else:
                lggr.debug(cmd.split('/')[-1] + ' directory synced.')
        print('Database synced successfully')

    def copy_dirs(self):
        """Copy the directories from patch folder to AppViewX location."""
        self.dirs_to_remove = ['Plugins', 'avxgw',
                               'jre', 'logs', 'properties',
                               'release_scripts', 'web']
        print('Copying new directories to AppViewX directory.')
        for directory in self.dirs_to_remove:
            try:
                shutil.copytree(
                    os.path.abspath(self.patch_path + '/' + directory),
                    os.path.abspath(self.appviewx_path + '/' + directory))
                lggr.debug('Copied ' + directory + ' to AppViewX location.')
            except:
                print('Unable to copy directory: ' + directory)
                lggr.error('Unable to copy directory: ' + directory)
        print('New directories copied to AppViewX directory.')

    def get_and_copy_license(self):
        """Get the license file and copy it to proper place."""
        import tarfile
        if os.path.isfile(
                current_file_location + '/../../../AppViewX_license.tar.gz'):
            license = os.path.abspath(
                current_file_location + '/../../../AppViewX_license.tar.gz')
        else:
            while True:
                license = os.path.abspath(
                    input('Enter the path of the license file: '))
                if os.path.isfile(license) and license.lower().endswith(
                        'license.tar.gz'):
                    break
        try:
            print('Copying license file to: ' + os.path.abspath(
                self.appviewx_path + '/avxgw'))
            shutil.copyfile(license, os.path.abspath(
                self.appviewx_path + '/avxgw/AppViewX_license.tar.gz'))
            lggr.debug(
                'license file copied to: ' + self.appviewx_path + '/avxgw')
        except:
            print('Unable to copy license file')
            return

        try:
            print('Extracting license')
            os.chdir(os.path.abspath(self.appviewx_path + '/avxgw'))
            tar = tarfile.open(
                os.path.abspath(
                    self.appviewx_path + '/avxgw/AppViewX_license.tar.gz'))
            tar.extractall()
            tar.close()
            print('License extracted.')
        except:
            print('Unable to extract license!')

    def initialize(self):
        """Initialize."""
        self.backup_old()
        self.conf_merge(merge=False)
        self.remove_old_directories()
        self.sync_directories()
        self.copy_dirs()
        self.conf_merge(merge=True)
        self.get_and_copy_license()

if __name__ == '__main__':
    user_input = sys.argv

    ob = ApplyPatch()
    ob.initialize()
