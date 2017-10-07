"""Script to change the state of components in monitor.conf."""
import configparser
import socket
import os
import logger
from using_fabric import AppviewxShell
from config_parser import config_parser
location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../conf"))
log_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../logs"))
logging = logger.avx_logger('monitorconfigure')
conf_data = config_parser(location + '/appviewx.conf')
hostname = socket.gethostbyname(socket.gethostname())


def update_monitor_conf(value=True):
        Config = configparser.ConfigParser()
        Config.read(location + "/monitor.conf")
        Config.set('CONFIGURATION', 'MONITOR', value)
        with open(location + '/monitor.conf', 'w') as configfile:
                Config.write(configfile)
        synchronise()


def watchdogs(user_input):
    """."""
    if 'operation' in user_input:
        user_input[1] = 'all'
    Config = configparser.ConfigParser()
    Config.read(location + "/monitor.conf")
    all_plugins = Config.options("PLUGINS")
    gateways = Config.options("GATEWAY")
    webs = Config.options("WEB")
    dbs = Config.options("MONGODB")
    logstashs = Config.options("LOGSTASH")
    if "--stop" in user_input[0]:
        if str(user_input[1]) in ["logstash", "all"]:
            if str(user_input[2]) == "all":
                for logstash in logstashs:
                    Config.set('LOGSTASH', logstash, "off")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info(
                            "{0} is being un-monitored".format(logstash))
            else:
                for logstash in logstashs:
                    gate_define = logstash.split(" ")
                    if str(user_input[2]) == gate_define[1]:
                        Config.set('LOGSTASH', logstash, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being un-monitored".format(logstash))
    if "--stop" in user_input[0]:
        if str(user_input[1]) in ["gateway", "all"]:
            if str(user_input[2]) == "all":
                for gateway in gateways:
                    Config.set('GATEWAY', gateway, "off")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info(
                            "{0} is being un-monitored".format(gateway))
            else:
                for gateway in gateways:
                    gate_define = gateway.split(" ")
                    if str(user_input[2]) == gate_define[1]:
                        Config.set('GATEWAY', gateway, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being un-monitored".format(gateway))
        if str(user_input[1]) in ["web", "all"]:
            if str(user_input[2]) == "all":
                for web in webs:
                    Config.set('WEB', web, "off")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being un-monitored".format(web))
            else:
                for web in webs:
                    web_define = web.split(" ")
                    if str(user_input[2]) == web_define[1]:
                        Config.set('WEB', web, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being un-monitored".format(web))
        if str(user_input[1]) in ["mongodb", "all"]:
            if str(user_input[2]) == "all":
                for db in dbs:
                    Config.set('MONGODB', db, "off")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being un-monitored".format(db))
            else:
                for db in dbs:
                    web_define = db.split(" ")
                    if str(user_input[2]) == web_define[1]:
                        Config.set('MONGODB', db, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being un-monitored".format(db))
        if str(user_input[1]) in ["plugins", "all"]:
            if str(user_input[2]) == "all":
                for plugs in all_plugins:
                    Config.set('PLUGINS', plugs, "off")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("%s is being un-monitored", plugs)
            elif len(user_input) == 3:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    if str(user_input[2]) in plug_define[0]:
                        Config.set('PLUGINS', plugs, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)

                            logging.info("%s is being un-monitored", plugs)
                    if str(user_input[2]) in plug_define[1]:
                        Config.set('PLUGINS', plugs, "off")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info("%s is being un-monitored", plugs)
            elif len(user_input) == 4:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    if str(user_input[2]) in plug_define[0]:
                        if str(user_input[3]) in plug_define[1]:
                            Config.set('PLUGINS', plugs, "off")
                            with open(
                                    location + '/monitor.conf', 'w'
                            ) as configfile:
                                Config.write(configfile)
                                logging.info("%s is being un-monitored", plugs)
            elif len(user_input) == 5:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    if str(user_input[2]) in plug_define[0]:
                        if str(user_input[3]) in plug_define[1]:
                            if str(user_input[4]) in plug_define[2]:
                                Config.set('PLUGINS', plugs, "off")
                                with open(
                                        location + '/monitor.conf', 'w'
                                ) as configfile:
                                    Config.write(configfile)
                                    logging.info(
                                        "%s is being un-monitored", plugs)
    elif user_input[0] in ["--start", "--restart"]:
        if str(user_input[1]) in ["logstash", "all"]:
            if str(user_input[2]) == "all":
                for logstash in logstashs:
                    Config.set('LOGSTASH', logstash, "on")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being monitored".format(logstash))
            else:
                for logstash in logstashs:
                    gate_define = logstash.split(" ")
                    if str(user_input[2]) == gate_define[1]:
                        Config.set('LOGSTASH', logstash, "on")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being monitored".format(logstash))
        if str(user_input[1]) in ["gateway", "all"]:
            if str(user_input[2]) == "all":
                for gateway in gateways:
                    Config.set('GATEWAY', gateway, "on")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being monitored".format(gateway))
            else:
                for gateway in gateways:
                    gate_define = gateway.split(" ")
                    if str(user_input[2]) == gate_define[1]:
                        Config.set('GATEWAY', gateway, "on")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info(
                                "{0} is being monitored".format(gateway))
        if str(user_input[1]) in ["web", "all"]:
            if str(user_input[2]) == "all":
                for web in webs:
                    Config.set('WEB', web, "on")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being monitored".format(web))
            else:
                for web in webs:
                    web_define = web.split(" ")
                    if str(user_input[2]) == web_define[1]:
                        Config.set('WEB', web, "on")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info("{0} is being monitored".format(web))
        if str(user_input[1]) in ["mongodb", "all"]:
            if str(user_input[2]) == "all":
                for db in dbs:
                    Config.set('MONGODB', db, "on")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("{0} is being monitored".format(db))
            else:
                for db in dbs:
                    web_define = db.split(" ")
                    if str(user_input[2]) == web_define[1]:
                        Config.set('MONGODB', db, "on")
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info("{0} is being monitored".format(db))

        if str(user_input[1]) in ["plugins", "all"]:
            if str(user_input[2]) == "all":
                for plugs in all_plugins:
                    Config.set('PLUGINS', plugs, "on")
                    with open(location + '/monitor.conf', 'w') as configfile:
                        Config.write(configfile)
                        logging.info("%s is being monitored", plugs)
            elif len(user_input) == 3:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    Config.set('PLUGINS', plugs, "on")
                    if str(user_input[2]) in plug_define[0:1]:
                        with open(
                                location + '/monitor.conf', 'w') as configfile:
                            Config.write(configfile)
                            logging.info("%s is being monitored", plugs)
            elif len(user_input) == 4:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    if str(user_input[2]) in plug_define[0]:
                        if str(user_input[3]) in plug_define[1]:
                            Config.set('PLUGINS', plugs, "on")
                            with open(
                                    location + '/monitor.conf', 'w'
                            ) as configfile:
                                Config.write(configfile)
                                logging.info("%s is being monitored", plugs)

            elif len(user_input) == 5:
                for plugs in all_plugins:
                    plug_define = plugs.split(" ")
                    if str(user_input[2]) in plug_define[0]:
                        if str(user_input[3]) in plug_define[1]:
                            if str(user_input[4]) in plug_define[2]:
                                Config.set('PLUGINS', plugs, "on")
                                with open(
                                        location + '/monitor.conf', 'w'
                                ) as configfile:
                                    Config.write(configfile)
                                    logging.info(
                                        "%s is being monitored", plugs)


def synchronise():
    """Send monitor.conf file across all nodes."""
    current_ip = socket.gethostbyname(socket.gethostname())
    ips = conf_data['ENVIRONMENT']['ips']
    from avx_commons import get_username_path
    for ip in ips:
        if not ip == current_ip:
            user, path = get_username_path(conf_data, ip)
            f_ob = AppviewxShell([ip], user=user)
            f_ob.file_send(
                location + '/monitor.conf', path + '/conf/monitor.conf')


def watchdog(user_input):
    """Start the monitoring process."""
    from configobj import ConfigObj
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    if '--start' in user_input:
        import configparser
        file = current_file_path + '/../../conf/monitor.conf'
        config = configparser.ConfigParser()
        config.read(file)
        config.set('CONFIGURATION', 'monitor', 'true')
        with open(file, 'w+') as configfile:
            config.write(configfile)
    if not os.path.isfile(current_file_path + '/../../conf/monitor.conf'):
        return
    conf = ConfigObj(current_file_path + '/../../conf/monitor.conf')
    try:
        res = conf['CONFIGURATION']['monitor'].lower()
    except:
        res = conf['CONFIGURATION']['MONITOR'].lower()
    if res != 'true' and '--start' not in user_input:
        return
    watchdogs(user_input)
    synchronise()
