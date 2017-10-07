"""
    This is the script which performs all the functions regarding the plugins
    upgrade like checking wheather its a new plugin or not and
    running the release.
    scripts accordingly and updating the version of the plugin
    in the database collection

"""

import os
from pymongo import MongoClient
import system
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

class PluginUpgrade(object):
    """
    This is the class which have all the fucntions for handling plugin
    upgrade check and it calls other scripts for jar execution.
    """

    @staticmethod
    def check_plugins_version(plugin_config):
        """
        Its method for checking the plugin version
        """

        with open(plugin_config, "r") as plugin:
            content = plugin.readlines()
            for line in content:
                if not line.startswith("#") and "VERSION" in line:
                        version = ((line.split("="))[1].strip("\n")).strip(" ")
        return version

    @staticmethod
    def new_or_old(plugin, version, mongo_port):
        """
        it checks whether its a new plugin or an old plugin.
        """
        new = "Not Present"
        old = ""
        client = MongoClient('localhost', int(mongo_port))
        mydb = client.appviewx
        for document in mydb.System_plugins.find():
            if plugin in document["Plugin"]:
                if not version in document["Version"]:
                    new = "Version Updated"
                    old = document["Version"]

                else:
                    new = "Present"
        return [new, client, old]

    def check_plugin_directory(self, plugins_path, port):
        """
        identifies all the plugins put inside the package
        """
        for plugin in os.listdir(plugins_path):
            new = False
            plugin_conf = plugins_path + "/" + plugin + "/conf/plugin.conf"
            if os.path.exists(plugin_conf):
                version = self.check_plugins_version(plugin_conf)
            else:
                print("Conf File does not exists for the plugin : " + plugin)
                system.exit(1)
            if version:
                new, client, old_version = self.new_or_old(
                    plugin, version, port)
            if new in ["Not Present", "Version Updated"]:
                print(
                    plugin +
                    "_" +
                    version +
                    " is new and now executing the Release scripts")
                # if new == "Version Updated":
                # jar_execute(fresh,plugin,version,old_version)
                # else:
                # jar_execute(fresh,plugin,version)
                self.update_plugin(plugin, version, new, client)
            else:
                print(plugin + "_" + version + "is not a new one")

    @staticmethod
    def update_plugin(plugin, version, new, client):
        """
        This Funtion will update the name of the plugin in the database
        """
        mydb = client.appviewx
        if "Version Updated" in new:
            update = mydb.System_plugins.find_one({'Plugin': plugin})
            update['Version'] = version
            mydb.System_plugins.save(update)
        elif "Not Present" in new:
            result = mydb.System_plugins.insert_one(
                {'_id': plugin, 'Plugin': plugin, 'Version': version})
            print([i for i in mydb.System_plugins.find()])
        else:
            print("Something Wrong happend")
if __name__ == '__main__':
    import sys
    args = sys.argv
    plugin = PluginUpgrade()
    plugin.check_plugin_directory(args[1], args[2])
