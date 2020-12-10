"""
SUPPORTED VARIABLES

#curtime#                   current time (h:m)
#timenow#                   current time (h:m)
#cpuload#                   CPU usage percentage
#ramload#                   RAM usage percentage
#name#                      user name
#nick#                      user name
#id#                        user id
#discriminator#             discriminator of tag
#servcount#                 guilds (servers) count
#guildcount#                guilds (servers) count
#friendcount#               friends count
#blockcount#                count of users in blocklist
#dayto:year.month.day#      days to specified date   | example: #dayto:2077.5.14#
#dayfrom:year.month.day#    days from specified date | example: #dayfrom:1999.2.20#
"""

import datetime
import re
import logging

import psutil
import requests

from constants import API_URL

class VariablesParser:

    def __init__(self, _thread):
        self._thread = _thread
        self.parsers = {
            "#curtime#": self.__timenow,
            "#timenow#": self.__timenow,
            "#cpuload#": self.__cpu_load,
            "#ramload#": self.__ram_load,
            "#name#": self.__nick,
            "#nick#": self.__nick,
            "#id#": self.__id,
            "#discriminator#": self.__discriminator,
            "#servcount#": self.__guilds_count,
            "#guildcount#": self.__guilds_count,
            "#friendcount#": self.__friend_count,
            "#blockcount#": self.__blocked_users_count,
            r"#dayto:(\d+\.\d{1,2}\.\d{1,2})#": self.__dayto,
            r"#dayfrom:(\d+\.\d{1,2}\.\d{1,2})#": self.__dayfrom,
        }
        self.cache = {}

    def parse_frame(self, frame):
        if re.search('(%s)' % '|'.join(self.parsers.keys()), frame["str"]):
            for var in self.parsers.keys():
                has_var = re.search(var, frame["str"])
                if has_var:
                    try:
                        var_value = str(self.parsers[var](variable=var, in_str=has_var))
                    except Exception as error:
                        logging.error("Failed to parse variable %s in frame: %s", var, repr(error))
                        self._thread.gui.current_info = self._thread.gui.lang_manager.get_string("parse_error") % (var, repr(error))
                        self._thread.gui.infoUpdated.emit()
                        continue
                    frame["str"] = re.sub(var, var_value, frame["str"])

        self.cache.clear()

        return frame

    def __timenow(self, **args):
        return datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")

    def __cpu_load(self, **args):
        return psutil.cpu_percent()

    def __ram_load(self, **args):
        return psutil.virtual_memory().percent

    def __nick(self, **args):
        if 'user' not in self.cache:
            self.cache['user'] = requests.get(API_URL + "/users/@me",
                                              headers=self._thread.auth("get"),
                                              proxies=self._thread.core.config.get('proxies')
                                             ).json(encoding="utf-8")

        return self.cache['user']['username']

    def __id(self, **args):
        if 'user' not in self.cache:
            self.cache['user'] = requests.get(API_URL + "/users/@me",
                                              headers=self._thread.auth("get"),
                                              proxies=self._thread.core.config.get('proxies')
                                             ).json(encoding="utf-8")

        return self.cache['user']['id']

    def __discriminator(self, **args):
        if 'user' not in self.cache:
            self.cache['user'] = requests.get(API_URL + "/users/@me",
                                              headers=self._thread.auth("get"),
                                              proxies=self._thread.core.config.get('proxies')
                                             ).json(encoding="utf-8")

        return self.cache['user']['discriminator']
    
    def __guilds_count(self, **args):
        if 'user_guilds' not in self.cache:
            self.cache['user_guilds'] = requests.get(API_URL + "/users/@me/guilds",
                                                     headers=self._thread.auth("get"),
                                                     proxies=self._thread.core.config.get('proxies')
                                                    ).json(encoding="utf-8")

        return len(self.cache['user_guilds'])

    def __friend_count(self, **args):
        if 'relationships' not in self.cache:
            self.cache['relationships'] = requests.get(API_URL + "/users/@me/relationships",
                                                       headers=self._thread.auth("get"),
                                                       proxies=self._thread.core.config.get('proxies')
                                                      ).json(encoding="utf-8")

        return len( list(filter(lambda x : x['type'] == 1, self.cache['relationships'] )) )

    def __blocked_users_count(self, **args):
        if 'relationships' not in self.cache:
            self.cache['relationships'] = requests.get(API_URL + "/users/@me/relationships",
                                                       headers=self._thread.auth("get"),
                                                       proxies=self._thread.core.config.get('proxies')
                                                      ).json(encoding="utf-8")

        return len( list(filter(lambda x : x['type'] == 2, self.cache['relationships'] )) )

    def __dayto(self, **args):
        parsed = re.findall(args["variable"], args["in_str"].group(0))[0].split(".")
        days = datetime.date(int(parsed[0]),int(parsed[1]),int(parsed[2])) - datetime.date.today()
        return str(days).split()[0]

    def __dayfrom(self, **args):
        parsed = re.findall(args["variable"], args["in_str"].group(0))[0].split(".")
        days =  datetime.date.today() - datetime.date(int(parsed[0]),int(parsed[1]),int(parsed[2]))
        return str(days).split()[0]
