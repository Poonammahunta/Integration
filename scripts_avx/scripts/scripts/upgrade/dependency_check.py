#!../Python/bin/python

import os
import sys
if not os.path.realpath('Commons/') in sys.path:
    sys.path.append(os.path.realpath('Commons/'))
import avx_commons
import set_path
avx_path = set_path.AVXComponentPathSetting()
from configobj import ConfigObj
from config_parser import config_parser
import avx_commons
import signal
from termcolor import colored
from distutils.version import StrictVersion
signal.signal(signal.SIGINT, avx_commons.sigint_handler)
current_file_location = os.path.dirname(os.path.realpath(__file__))
conf_data = config_parser(current_file_location + '/../../conf/appviewx.conf')
plugins = conf_data['PLUGINS']['plugins']


def dependency_check(dependency_list):
    not_satisfied = []
    conf_data = config_parser(current_file_location + '/../../conf/appviewx.conf')
    db = avx_commons.db_connection(conf_data,True)
    avx_db = db['appviewx']
    if not 'system_plugins' in avx_db.collection_names():
        not_satisfied.append(
            'system_plugins collection is missing in appviewx database')
        return not_satisfied
    db_coll = avx_db['system_plugins']
    for each_dependency_plugin in dependency_list.keys():
        plugin = each_dependency_plugin
        min_expected_version = dependency_list[each_dependency_plugin]['min']
        max_expected_version = dependency_list[each_dependency_plugin]['max']
        m = db_coll.find({"Plugin": plugin})
        if m.count() == 0:
            not_satisfied.append('Plugin : %s is not installed' % plugin)
        elif m.count() > 1:
            not_satisfied.append(
                'Plugin : %s has multiple entries in System_plugins collection ' %
                plugin)
        else:
            try:
                installed_version = m[0]["Version"]
            except KeyError:
                not_satisfied.append(
                    'Version is not found for the plugin : %s in the database' %
                    plugin)
                continue
            if min_expected_version == 'None':
                min_expected_version = False
            if max_expected_version == 'None':
                max_expected_version = False
            if min_expected_version and StrictVersion(installed_version) < StrictVersion(min_expected_version):
                not_satisfied.append(
                    ' %s needs higher version(%sV) to upgrade.(Installed version : %s)' %
                    (plugin.title(), min_expected_version, installed_version))
            if max_expected_version and StrictVersion(installed_version) > StrictVersion(max_expected_version):
                not_satisfied.append(
                    ' %s needs lower version(%sV) to upgrade.(Installed version : %s)' %
                    (plugin.title(), max_expected_version, installed_version))

    return not_satisfied


def get_plugin_details():
    """."""
    try:
        db = avx_commons.db_connection(conf_data,True)
        for plugin in plugins:
            if not os.path.isdir(avx_path.plugin_path):
                print("Plugin directory not found : %s" % avx_path.plugin_path)
                continue
            if not os.path.isdir(avx_path.plugin_path + str(plugin)):
                print(
                    "Plugin directory not found : %s" %
                    avx_path.plugin_path +
                    str(plugin))
                continue
            plugin_conf_file = avx_path.plugin_path + \
                str(plugin) + "/" + plugin + ".conf"
            config = ConfigObj(plugin_conf_file)
            try:
                if len(config['VERSION']) == 0:
                    raise ValueError
            except ValueError:
                print(
                    colored(
                        "VERSION field value is empty in plugin conf file(%s)" %
                        plugin_conf_file,
                        "red"))
                continue
            except Exception as e:
                print(
                    colored(
                        "VERSION field is missing in plugin conf file(%s)" %
                        plugin_conf_file,
                        "red"))
                continue

            avx_db = db['appviewx']
            doc_structure = {
                "_id": plugin,
                "Plugin": plugin,
                "Version": config['VERSION']}
            try:
                avx_db.system_plugins.save(doc_structure)
            except Exception as e:
                print(
                    colored("Error in inserting data into System_plugins collection in avx db"))
                print("data: %s" % doc_structure)
                continue
    except Exception as e:
        print(e)
        return False
    return True
dependency_check({'avx-common': {'min': 'None', 'max': '5.0.0'}})
