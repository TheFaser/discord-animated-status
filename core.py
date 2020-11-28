import json
import logging
import random
import time
from datetime import datetime

import requests

from PyQt5.QtCore import QThread

from constants import API_URL

class Core(object):
    """Back-End class."""

    def __init__(self, gui):
        self.gui = gui
        self.config = {}
        self.statistics = {}

    def config_load(self):
        """Loads the settings from a config file."""
        logging.info('Reading config file...')
        try:
            with open("config.json", "r", encoding="utf-8") as cfg_file:
                config = json.load(cfg_file)

            logging.info('Config file loaded.')

        except FileNotFoundError:
            logging.info("Config file not found. Reading old config file...")
            config = self.load_old_config()
            if not config:
                logging.info("Creating default config...")
                config = {"token": "", "frames": [], "delay": 3, "language": "en", "tray_notifications": True, "proxies": {"https": ""}}
                self.config_save(gui_emit=False, old_file=False, config=config)

        except Exception as error:
            logging.error("Failed to read config file: %s", repr(error))
            config = self.load_old_config()
            if not config:
                logging.info("Creating default config...")
                config = {"token": "", "frames": [], "delay": 3, "language": "en", "tray_notifications": True, "proxies": {"https": ""}}
                self.config_save(gui_emit=False, old_file=False, config=config)

        finally:
            self.config = config.copy()

        if "frames" not in self.config:
            self.config["frames"] = []
        elif not isinstance(self.config["frames"], list):
            logging.critical('Invalid config: frames must be a list')

        try:
            if self.config["delay"] < 1:
                self.config["delay"] = 3
        except (KeyError, TypeError):
            self.config["delay"] = 3

        if 'randomize_frames' not in self.config:
            self.config['randomize_frames'] = False

        if 'language' not in self.config:
            self.config['language'] = "en"

        if "tray_notifications" not in self.config:
            self.config["tray_notifications"] = True

        if "proxies" not in self.config:
            self.config["proxies"] = {"https": ""}
        elif not isinstance(self.config["proxies"], dict):
            logging.critical('Invalid config: proxies must be a dict')

        if config != self.config:
            self.config_save(gui_emit=False)

    def apply_config(self):
        self.gui.speed_edit.setValue(self.config['delay'])
        self.gui.frames_list_edit_filling()
        if self.config['randomize_frames']:
            self.gui.randomize_frames_checkbox.toggle()

    def load_old_config(self):
        logging.info('Reading config.old file...')
        try:
            with open("config.old.json", "r", encoding="utf-8") as cfg_file:
                config = json.load(cfg_file)
            logging.info('config.old file loaded.')

        except FileNotFoundError:
            logging.info("config.old file not found.")
            config = {}

        except Exception as error:
            logging.error("Failed to read config.old file: %s", repr(error))
            config = {}

        return config

    def config_save(self, gui_emit=True, old_file=True, config=None):
        """Saves the settings to a config file."""
        logging.info('Config file saving...')

        if not config:
            config = self.config

        try:
            if old_file:
                try:
                    with open("config.json", "r", encoding="utf-8") as cfg_file:
                        old_config = json.load(cfg_file)

                    with open("config.old.json", "w", encoding="utf-8") as cfg_file:
                        json.dump(old_config, cfg_file, ensure_ascii=False, indent=4)

                    logging.info('config.old file saved.')

                except Exception as error:
                    logging.error("Failed to save old config: %s", repr(error))
                    if gui_emit:
                        self.gui.current_info = self.gui.lang_manager.get_string("save_error")
                        self.gui.custom_signal.infoUpdated.emit()

            with open("config.json", "w", encoding="utf-8") as cfg_file:
                json.dump(config, cfg_file, ensure_ascii=False, indent=4)

            logging.info('Config file saved.')

        except Exception as error:
            logging.error("Failed to save config: %s", repr(error))
            if gui_emit:
                self.gui.current_info = self.gui.lang_manager.get_string("save_error")
                self.gui.custom_signal.infoUpdated.emit()

    def save_statistics(self):
        """Saves the settings to a config file."""
        logging.info('Statistics file saving...')
        try:
            with open("statistics.json", "w", encoding="utf-8") as json_file:
                json.dump(self.statistics, json_file, ensure_ascii=False)

            logging.info('Statistics file saved.')

        except Exception as error:
            logging.error("Failed to save statistics: %s", repr(error))

    def load_statistics(self):
        """Loads the statistics from a file."""
        logging.info('Reading statistics file...')
        try:
            with open("statistics.json", "r", encoding="utf-8") as json_file:
                self.statistics = json.load(json_file)

            logging.info('Statistics file loaded.')

        except FileNotFoundError:
            logging.info("Statistics file not found.")
            self.statistics = {"total_requests_count": 0, "last_session_requests": 0}
            self.save_statistics()

        except Exception as error:
            logging.error("Failed to load statistics file: %s", repr(error))
            self.statistics = {"total_requests_count": 0, "last_session_requests": 0}

            with open("statistics.json", "w", encoding="utf-8") as json_file:
                json.dump(self.statistics, json_file, indent=4, ensure_ascii=False)

class RequestsThread(QThread):

    def __init__(self, core, gui):
        super().__init__()
        self.core = core
        self.gui = gui

    def parse_frame(self, frame):
        """Parse animated status frame."""
        now = datetime.now()
        try:
            mydata = requests.get(API_URL + "/users/@me", headers=self.auth("get"),
                                  proxies=self.core.config.get('proxies')).json(encoding="utf-8")
            frame["str"] = frame["str"].replace("#curtime#", datetime.strftime(now, "%H:%M"))
            servcount = len(requests.get(API_URL + "/users/@me/guilds", headers=self.auth("get"),
                                         proxies=self.core.config.get('proxies')).json(encoding="utf-8"))
            frame["str"] = frame["str"].replace("#servcount#", str(servcount))
            frame["str"] = frame["str"].replace("#name#", mydata["username"])
            frame["str"] = frame["str"].replace("#id#", mydata["discriminator"])
        except (KeyError, TypeError, requests.exceptions.RequestException) as e:
            frame = {"str": "Error", "emoji": ""}
            logging.error("Failed to parse frame: %s", repr(e))
            self.gui.current_info = "%s: %s" % (self.gui.lang_manager.get_string("parse_error"), repr(e))
            self.gui.custom_signal.infoUpdated.emit()

    def auth(self, method):
        """Creates and returns a header for discord API using current token."""
        try:
            return {"Authorization": self.core.config["token"], "Content-Type": "application/json", "method": method.upper()}
        except (KeyError, TypeError) as e:
            logging.error("Failed to create authorization header: %s", e)
            return None

    def run(self):
        """Animated status thread target."""
        self.core.statistics['last_session_requests'] = 0
        self.core.save_statistics()

        i = -1
        while True:
            if self.core.config['randomize_frames']:
                i = random.randint(0, len(self.core.config['frames']) - 1)
                frame = self.core.config['frames'][i]
            else:
                i += 1
                if i >= len(self.core.config['frames']):
                    i = 0
                frame = self.core.config["frames"][i]

            # useless requests are disabled if string variables not found in frame
            for var in ('#curtime#', '#servcount#', '#name#', '#id#'):
                if var in frame['str']:
                    self.parse_frame(frame)
                    break

            p_params = json.dumps({"custom_status": {"text": frame.get("str"),
                                                     "emoji_id": frame.get('custom_emoji_id'),
                                                     "emoji_name": frame.get('emoji'),
                                                     "expires_at": None}})

            try:
                req = requests.patch(API_URL + "/users/@me/settings",
                                     headers=self.auth("patch"), data=p_params,
                                     proxies=self.core.config.get('proxies'))
                if req.status_code == 200:
                    if not frame["emoji"] and not frame.get('custom_emoji_id'):
                        self.gui.current_frame = frame["str"]
                    elif frame.get('custom_emoji_id'):
                        self.gui.current_frame = "C | " + frame["str"]
                    else:
                        self.gui.current_frame = frame["emoji"] + " | " + frame["str"]
                    self.gui.custom_signal.frameUpdated.emit()
                    if self.gui.current_info != "":
                        self.gui.current_info = ""
                        self.gui.custom_signal.infoUpdated.emit()
                elif req.status_code == 429:  # Never create request overflow
                    logging.error("Discord XRate exceeded. Sleeping for 30 to let Discord rest.")
                    self.gui.current_info = self.gui.lang_manager.get_string("xrate_exceeded")
                    self.gui.custom_signal.infoUpdated.emit()
                    if self.core.config["tray_notifications"]:
                        self.gui.tray_icon.showMessage("Discord Animated Status", self.gui.lang_manager.get_string("xrate_exceeded"), self.gui.icon, msecs=1000)
                    time.sleep(30)
                elif req.status_code == 401:
                    logging.error("Failed to authorize in Discord. Thread stopping...")
                    self.gui.custom_signal.authFailed.emit()
                    return
                elif req.status_code == 400:
                    logging.error("Bad Request (400)")
                    self.gui.current_info = "Bad Request (400)"
                    self.gui.custom_signal.infoUpdated.emit()
                    self.gui.current_frame = frame['str']
                    self.gui.custom_signal.frameUpdated.emit()

            except requests.exceptions.RequestException as e:
                logging.error("A request error occured: %s", repr(e))
                self.gui.current_info = "%s: %s" % (self.gui.lang_manager.get_string("error"), repr(e))
                self.gui.custom_signal.infoUpdated.emit()
                if self.core.config["tray_notifications"]:
                    self.gui.tray_icon.showMessage("Discord Animated Status", "%s: %s" % (self.gui.lang_manager.get_string("error"), repr(e)), self.gui.icon, msecs=1000)

            self.core.statistics['total_requests_count'] += 1
            self.core.statistics['last_session_requests'] += 1
            self.core.save_statistics()

            time.sleep(self.core.config["delay"])
