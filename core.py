from required import json, logging, requests, datetime, api_url, time

class Core(object):
    """Back-End class."""

    def __init__(self, gui):
        self.config = {}
        self.gui = gui
        self.stop_thread = False

    def config_load(self):
        """Loads the settings from a config file."""
        try:
            with open("config.json", "r+", encoding="utf-8") as cfg_file:
                self.config = json.load(cfg_file)
        except:
            self.config = {"token": "", "frames": [], "delay": 3, "language": "en", "hide_token_input": False, "tray_notifications": True}

        try:
            self.gui.token_input.setText(str(self.config["token"]))
            self.gui.token_input.setToolTip(self.gui.lang_manager.get_string("your_token_tooltip") + str(self.config["token"]))
        except KeyError:
            self.config.update({"token": ""})

        if "frames" not in self.config:
            self.config.update({"frames": []})
        if type(self.config["frames"]) != list:
            self.config["frames"] = []
        self.gui.frames_list_edit_filling()

        try:
            if self.config["delay"] < 1:
                self.config["delay"] = 3
            self.gui.speed_edit.setValue(self.config["delay"])
        except KeyError:
            self.config.update({"delay": 3})
            self.gui.speed_edit.setValue(3)
        except:
            self.config["delay"] = 3
            self.gui.speed_edit.setValue(3)

        try:
            if self.config["language"] in self.gui.lang_manager.supported_langs:
                self.gui.lang_manager.selected_lang = self.config["language"]
            else:
                self.gui.lang_manager.selected_lang = "en"
        except KeyError:
            self.config.update({"language": "en"})
        except:
            self.config["language"] = "en"

        try:
            if self.config["hide_token_input"] == True:
                self.gui.resize(400, 250)
            else:
                self.gui.resize(400, 280)
        except:
            self.config.update({"hide_token_input": False})
            self.gui.resize(400, 280)

        if "tray_notifications" not in self.config:
            self.config.update({"tray_notifications": True})

        
        with open("config.json", "w", encoding="utf-8") as cfg_file:
             json.dump(self.config, cfg_file, indent=4, ensure_ascii=False)
    
    def parse_frame(self, frame):
        """Parse animated status frame."""
        now = datetime.now()
        try:
            mydata = requests.get(api_url+"/users/@me", headers=self.auth("get")).json(encoding="utf-8")
            frame["str"] = frame["str"].replace( "#curtime#", datetime.strftime(now, "%H:%M"))
            servcount = len(requests.get(api_url+"/users/@me/guilds", headers=self.auth("get")).json(encoding="utf-8"))
            frame["str"] = frame["str"].replace("#servcount#", str(servcount))
            frame["str"] = frame["str"].replace("#name#", mydata["username"])
            frame["str"] = frame["str"].replace("#id#", mydata["discriminator"])
        except (KeyError, TypeError, requests.exceptions.RequestException) as e:
            frame = {"str": "Error", "emoji": ""}
            logging.error("Failed to parse frame: %s", e)
            self.gui.current_info = "%s: %s" % (self.gui.lang_manager.get_string("parse_error"), e)
            self.gui.custom_signal.infoUpdated.emit()

    def auth(self, method):
        """Creates and returns a header for discord API using current token."""
        try:
            return {"Authorization": self.config["token"], "Content-Type": "application/json", "method": method.upper()}
        except (KeyError, TypeError) as e:
            logging.error("Failed to create authorization header: %s", e)
            return None

    def config_save(self):
        """Saves the settings to a config file."""
        try:
            with open("config.json", "w", encoding="utf-8") as cfg_file:
                json.dump(self.config, cfg_file, ensure_ascii=False, indent=4)
        except:
            logging.error("Failed to save config.")
            self.gui.current_info = self.gui.lang_manager.get_string("save_error")
            self.gui.custom_signal.infoUpdated.emit()

    def run_animated_status(self):
        """Animated status thread target."""
        while True:
            for item in self.config["frames"]:
                frame = item.copy()
                self.parse_frame(frame)
                p_params = json.dumps({"custom_status": {"text": frame["str"], "emoji_id": None, "emoji_name": frame["emoji"], "expires_at": None}})
                try:
                    req = requests.patch(api_url+"/users/@me/settings", headers=self.auth("patch"), data=p_params)
                    if req.status_code == 200:
                        pass
                        if frame["emoji"] == "":
                            self.gui.current_frame = frame["str"]
                        else:
                            self.gui.current_frame = frame["emoji"] + " | " + frame["str"]
                        self.gui.custom_signal.frameUpdated.emit()
                        if self.gui.current_info != "":
                            self.gui.current_info = ""
                            self.gui.custom_signal.infoUpdated.emit()
                    elif req.status_code == 429:  # Never create request overflow
                        logging.error("Discord XRate exceeded. Sleeping for 30s to let Discord rest.")
                        self.gui.current_info = self.gui.lang_manager.get_string("xrate_exceeded")
                        self.gui.custom_signal.infoUpdated.emit()
                        if self.config["tray_notifications"]:
                            self.gui.tray_icon.showMessage("Discord Animated Status", self.gui.lang_manager.get_string("xrate_exceeded"), self.icon, msecs=1000)
                        if self.stop_thread == True:
                            return
                        time.sleep(30)

                except requests.exceptions.RequestException as e:
                    logging.error("A request error occured: %s", e)
                    self.gui.current_info = "%s%s" % (self.gui.lang_manager.get_string("request_error"), e)
                    self.gui.custom_signal.infoUpdated.emit()
                    if self.config["tray_notifications"]:
                        self.gui.tray_icon.showMessage("Discord Animated Status", "%s%s" % (self.gui.lang_manager.get_string("request_error"), e), self.gui.icon, msecs=1000)
                    continue

                if self.stop_thread == True:
                    return
                time.sleep(self.config["delay"])
