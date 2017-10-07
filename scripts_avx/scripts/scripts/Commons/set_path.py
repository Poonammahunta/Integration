#!/usr/bin/python

import os
import signal
# signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class AVXComponentPathSetting(object):

    def __init__(self):
        self.appviewx_path = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))) + "/"
        self.conf_folder_path = self.appviewx_path + '/conf'
        self.conf_file_path = self.conf_folder_path + '/appviewx.conf'
        self.gateway_path = self.appviewx_path + '/avxgw/'
        self.db_path = self.appviewx_path + '/db/'
        self.db_bin_path = self.appviewx_path + '/db/mongodb/bin/'
        self.mongo_restore = self.appviewx_path + '/db/mongodb/bin/mongorestore'
        self.mongo_dump = self.appviewx_path + '/db/mongodb/bin/mongodump'
        self.java_path = self.appviewx_path + '/jre/bin/java'
        self.log_path = self.appviewx_path + '/logs/'
        self.property_path = self.appviewx_path + '/properties/'
        self.python_path = self.appviewx_path + '/Python/bin/python'
        self.release_scripts_path = self.appviewx_path + '/release_scripts/'
        self.web_path = self.appviewx_path + '/web/'
        self.web_apache_path = self.appviewx_path + '/web/apache-tomcat-web/'
        self.script_path = self.appviewx_path + '/web/apache-karaf-service/'
        self.plugin_path = self.appviewx_path + '/Plugins/'
