import json
import logging
import random
import time
from datetime import datetime

import asyncio

import requests
import pypresence

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt

from constants import API_URL

class Core(object):
    """Back-End class."""

    def __init__(self, gui):
        self.gui = gui
        self.config = {}
        self.statistics = {}

        self.rpc = None
        self.rpc_thread = QThread()

        self.clock = QTimer()
        self.clock.setTimerType(Qt.PreciseTimer)
        self.clock.setInterval(100)
        self.clock.timeout.connect(self.on_clock_tick)

        self.string_constants = {'#APP_LAUNCH#': int(time.time())}

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

        if "rpc_client_id" not in self.config:
            self.config["rpc_client_id"] = ""

        if "disable_rpc" not in self.config:
            self.config["disable_rpc"] = True

        if 'default_rpc' not in self.config:
            self.config['default_rpc'] = {}
            self.config['default_rpc']['state'] = ''
            self.config['default_rpc']['details'] = ''
            self.config['default_rpc']['start_timestamp'] = ''
            self.config['default_rpc']['end_timestamp'] = ''
            self.config['default_rpc']['large_image_key'] = ''
            self.config['default_rpc']['large_image_text'] = ''
            self.config['default_rpc']['small_image_key'] = ''
            self.config['default_rpc']['small_image_text'] = ''
        elif not isinstance(self.config['default_rpc'], dict):
            logging.critical('Invalid config: default_rpc must be a dict')

        if "proxies" not in self.config:
            self.config["proxies"] = {"https": ""}
        elif not isinstance(self.config["proxies"], dict):
            logging.critical('Invalid config: proxies must be a dict')

        if config != self.config:
            self.config_save(gui_emit=False)

    def apply_config(self):
        logging.info('Config applying...')
        self.gui.speed_edit.setValue(self.config['delay'])
        self.gui.frames_list_edit_filling()
        if self.config['randomize_frames']:
            self.gui.randomize_frames_checkbox.toggle()
        if self.config['rpc_client_id'] and not self.config['disable_rpc']:
            if self.rpc:
                if self.rpc.client_id != str(self.config['rpc_client_id']):
                    self.disconnect_rpc()
                    self.connect_rpc()
            else:
                self.connect_rpc()

        else:
            if self.rpc:
                self.disconnect_rpc()

        logging.info('Config applied.')

    def connect_rpc(self):
        self.rpc = RichPresenceCustom(self.config['rpc_client_id'], self.string_constants)
        self.rpc_thread.start()
        self.rpc.moveToThread(self.rpc_thread)
        self.rpc.start_connect.connect(self.rpc.run)
        self.rpc.start_connect.emit()
        self.clock.start()

    def disconnect_rpc(self):
        try:
            if self.rpc.loop.is_running():
                self.rpc.loop.stop()
            else:
                try:
                    self.rpc.close()
                except AttributeError:
                    self.rpc.loop.stop()
        except Exception as error:
            logging.error('Failed to close RPC: %s', repr(error))

        self.rpc_thread.quit()
        self.rpc.deleteLater()

    def on_clock_tick(self):
        if self.rpc.error:
            if self.rpc.error.is_critical:
                self.clock.stop()
                return

        if self.rpc.is_connected:
            logging.info('Discord RPC connected.')
            self.clock.stop()
            if not self.config['disable_rpc']:
                try:
                    self.rpc.update_rpc(self.config['default_rpc'])
                except Exception as error:
                    logging.error("Failed to update Discord RPC: %s", repr(error))

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
        try:
            frame["str"] = frame["str"].replace("#curtime#", datetime.strftime(datetime.now(), "%H:%M"))

            if ('#name#' in frame["str"]) or ('#id#' in frame['str']):
                mydata = requests.get(API_URL + "/users/@me", headers=self.auth("get"),
                                      proxies=self.core.config.get('proxies')).json(encoding="utf-8")
                frame["str"] = frame["str"].replace("#name#", mydata["username"])
                frame["str"] = frame["str"].replace("#id#", mydata["discriminator"])

            if '#servcount#' in frame['str']:
                servcount = len(requests.get(API_URL + "/users/@me/guilds", headers=self.auth("get"),
                                             proxies=self.core.config.get('proxies')).json(encoding="utf-8"))
                frame["str"] = frame["str"].replace("#servcount#", str(servcount))

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
                frame = self.core.config['frames'][i].copy()
            else:
                i += 1
                if i >= len(self.core.config['frames']):
                    i = 0
                frame = self.core.config["frames"][i].copy()

            # useless requests are disabled if string variables not found in frame
            for var in ('#curtime#', '#servcount#', '#name#', '#id#'):
                if var in frame['str']:
                    self.parse_frame(frame)
                    break

            p_params = json.dumps({"custom_status": {"text": frame.get("str"),
                                                     "emoji_id": frame.get('custom_emoji_id') if frame.get('custom_emoji_id') else None,
                                                     "emoji_name": frame.get('emoji') if frame.get('emoji') else None,
                                                     "expires_at": None}})

            try:
                if not self.core.config['disable_rpc']:
                    if self.core.rpc.is_connected:
                        if ''.join(list(frame.get('rpc', {}).values())):
                            try:
                                self.core.rpc.update_rpc(frame.get('rpc'))
                            except Exception as error:
                                logging.error("Failed to update Discord RPC: %s", repr(error))
                                self.gui.current_info = "RPC update failed:\n%s" % repr(error)
                                self.gui.custom_signal.infoUpdated.emit()

                req = requests.patch(API_URL + "/users/@me/settings",
                                     headers=self.auth("patch"), data=p_params,
                                     proxies=self.core.config.get('proxies'))
                if req.status_code == 200:
                    item = frame.copy()
                    if item.get('custom_emoji_id'):
                        item['custom_emoji_id'] = 'C'
                        item['emoji'] = ''
                    if ''.join(list(item.get('rpc', {}).values())):
                        item['rpc'] = 'RPC'

                    self.gui.current_frame = ' | '.join([e for e in reversed(list(item.values())) if e])
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
                    self.sleep(30)
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

            self.sleep(self.core.config["delay"])

class RichPresenceCustom(pypresence.Presence, QObject):

    __slots__ = 'is_connected', 'error', 'string_constants',

    start_connect = pyqtSignal()

    def __init__(self, client_id, string_constants):
        QObject.__init__(self)
        pypresence.Presence.__init__(self, client_id=client_id, loop=asyncio.new_event_loop())
        self.is_connected = False
        self.error = None
        self.string_constants = string_constants

    @pyqtSlot()
    def run(self):
        logging.info('Discord RPC connecting...')
        try:
            self.connect()
            self.is_connected = True
            self.error = None

        except Exception as error:
            logging.error('Failed to connect RPC: %s', repr(error))
            if self.error:
                self.error = RichPresenceConnectError(error, is_critical=True)
            else:
                self.error = RichPresenceConnectError(error)
                logging.info('20 seconds pause to try connect RPC...')
                self.thread().sleep(20)
                return self.run()

    def update_rpc(self, config):
        config = config.copy()
        config['start_timestamp'] = self._convert_variables(config['start_timestamp'])
        config['end_timestamp'] = self._convert_variables(config['end_timestamp'])

        self.update(
            state=config['state'] if config['state'] else None,
            details=config['details'] if config['details'] else None,
            start=config['start_timestamp'] if config['start_timestamp'] else None,
            end=config['end_timestamp'] if config['end_timestamp'] else None,
            large_image=config['large_image_key'] if config['large_image_key'] else None,
            large_text=config['large_image_text'] if config['large_image_text'] else None,
            small_image=config['small_image_key'] if config['small_image_key'] else None,
            small_text=config['small_image_text'] if config['small_image_text'] else None)

        logging.info('Discord RPC updated.')

    def _convert_variables(self, string):
        if not string:
            return string
        if not isinstance(string, str):
            return string

        string_variables = self.string_constants.copy()
        string_variables['#NOW#'] = int(time.time())

        for variable in string_variables:
            string = string.replace(variable, str(string_variables[variable]))

        try:
            string = eval(string)
        except Exception as error:
            logging.error('Failed to evaluate string expression: %s', repr(error))
            string = ''

        return string

class RichPresenceConnectError(Exception):

    def __init__(self, base_exception, is_critical=False):
        self.base_exception = base_exception
        self.is_critical = is_critical

        if isinstance(self.base_exception, pypresence.InvalidPipe):
            self.message = 'Running discord app not found'
            self.lang_string = 'discord_not_found'
        else:
            self.message = 'An error has occured'
            self.lang_string = 'rpc_error_see_log'

        super().__init__(self.message)
