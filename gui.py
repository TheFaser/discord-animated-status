from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from required import *
from lang import LanguageManager

class App(QWidget):
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.mainWindow()

    def restart(self):
        """Restarts the program."""
        logging.info("Forced restart. Restarting...")
        self.config_save()
        self.tray_icon.hide()
        scr = sys.executable
        os.execl(scr, scr, *sys.argv)

    def make_lang_callback(self, lang):
        """Method factory for menu bar language selection."""
        def f():
            self.lang_manager.selected_lang = lang
            self.config["language"] = self.lang_manager.selected_lang
            self.restart()
        return f

    def mainWindow(self):
        """Initialize application layout."""
        self.setMinimumSize(QSize(400, 250))
        self.setMaximumSize(QSize(400, 280))

        self.lang_manager.load_language()

        # + PRESETS SECTION

        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont("res/uni-sans.ttf")
        self.btnFontFamily = font_db.applicationFontFamilies(font_id)[0]

        self.font14 = QFont()
        self.font14.setPointSize(14)

        self.font10 = QFont()
        self.font10.setFamily(self.btnFontFamily)
        self.font10.setPointSize(10)

        self.font9 = QFont()
        self.font9.setPointSize(9)

        self.font8 = QFont()
        self.font8.setPointSize(8)

        self.font7 = QFont()
        self.font7.setFamily("Consolas")
        self.font7.setBold(True)
        self.font7.setPointSize(12)

        self.setWindowTitle("Discord Animated Status")
        self.icon = QIcon("res/icon.ico")
        self.setWindowIcon(self.icon)

        self.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        # + END PRESETS SECTION

        # + TRAY SECTION

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip("Discord Animated Status")

        menu = QMenu()
        self.run_stop_animated_status = menu.addAction(self.lang_manager.get_string("launch"))
        self.exit_the_program = menu.addAction(self.lang_manager.get_string("quit"))

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # + END TRAY SECTION

        # + MAIN SECTION

        # ++ MENU BAR SECTION

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setFont(self.font9)

        self.menu_bar_config = self.menu_bar.addMenu(self.lang_manager.get_string("config"))
        self.menu_bar_config_load = QAction(self.lang_manager.get_string("load"), self)
        self.menu_bar_config_load.triggered.connect(self.config_load)
        self.menu_bar_config_save = QAction(self.lang_manager.get_string("save"), self)
        self.menu_bar_config_save.triggered.connect(self.config_save)
        self.menu_bar_config.addAction(self.menu_bar_config_save)
        self.menu_bar_config.addAction(self.menu_bar_config_load)

        self.menu_bar_language = self.menu_bar.addMenu(self.lang_manager.get_string("language"))
        for lang in self.lang_manager.supported_langs:  # For each supported language
            # Create action with the language
            if lang == self.lang_manager.selected_lang:
                act = QAction(lang.upper() + "    <", self)
            else:
                act = QAction(lang.upper(), self)
            # Create and connect a callback method for this language
            act.triggered.connect(self.make_lang_callback(lang))
            self.menu_bar_language.addAction(act)  # Add action to the menu

        self.about_act = QAction(self.lang_manager.get_string("about"), self)
        self.about_act.triggered.connect(self.about)
        self.menu_bar_about = self.menu_bar.addAction(self.about_act)

        # ++ END MENU BAR SECTION

        # ++ FRAME LIST SECTION

        self.frames_list_edit = QListWidget(self)
        self.frames_list_edit.move(10, 25)
        self.frames_list_edit.resize(200, 185)
        self.frames_list_edit.setToolTip(self.lang_manager.get_string("animated_frame_list"))

        self.moveUp_frame_btn = QPushButton("U", self)
        self.moveUp_frame_btn.resize(25, 25)
        self.moveUp_frame_btn.move(10, 216)
        self.moveUp_frame_btn.setFont(self.font14)
        self.moveUp_frame_btn.setToolTip(self.lang_manager.get_string("move_up_tooltip"))

        self.moveDown_frame_btn = QPushButton("D", self)
        self.moveDown_frame_btn.resize(25, 25)
        self.moveDown_frame_btn.move(40, 216)
        self.moveDown_frame_btn.setFont(self.font14)
        self.moveDown_frame_btn.setToolTip(self.lang_manager.get_string("move_down_tooltip"))

        self.frames_clear_btn = QPushButton(self.lang_manager.get_string("clear"), self)
        self.frames_clear_btn.resize(80, 25)
        self.frames_clear_btn.move(70, 216)
        self.frames_clear_btn.setFont(self.font10)
        self.frames_clear_btn.setToolTip(self.lang_manager.get_string("clear_tooltip"))

        self.add_frame_btn = QPushButton("+", self)
        self.add_frame_btn.resize(25, 25)
        self.add_frame_btn.move(155, 216)
        self.add_frame_btn.setFont(self.font10)
        self.add_frame_btn.setToolTip(self.lang_manager.get_string("add_frame"))

        self.remove_frame_btn = QPushButton("-", self)
        self.remove_frame_btn.resize(25, 25)
        self.remove_frame_btn.move(185, 216)
        self.remove_frame_btn.setFont(self.font10)
        self.remove_frame_btn.setToolTip(self.lang_manager.get_string("remove_selected_frame"))

        # ++ END FRAME LIST SECTION

        # ++ CURRENT FRAME SECTION

        lbl = QLabel(self.lang_manager.get_string("current_frame"), self)
        lbl.setFont(self.font9)
        lbl.setAlignment(Qt.AlignCenter)
        #txt_width = lbl.fontMetrics().boundingRect(lbl.text()).width()
        lbl.move(225, 15)

        self.current_frame_screen = QTextBrowser(self)
        self.current_frame_screen.resize(167, 40)
        self.current_frame_screen.move(222, 32)
        self.current_frame_screen.setFont(self.font8)
        self.current_frame_screen.setToolTip(self.lang_manager.get_string("current_displayed_frame"))

        # ++ END CURRENT FRAME SECTION

        # ++ INFO SECTION

        lbl = QLabel(self.lang_manager.get_string("info"), self)
        lbl.move(240, 75)
        lbl.setFont(self.font9)

        self.info_screen = QTextBrowser(self)
        self.info_screen.resize(167, 40)
        self.info_screen.move(222, 92)
        self.info_screen.setFont(self.font8)
        self.info_screen.setToolTip(self.lang_manager.get_string("more_info"))

        # ++ END INFO SECTION

        # ++ DELAY SECTION

        lbl = QLabel(self.lang_manager.get_string("delay_s"), self)
        lbl.move(224, 150)
        lbl.setFont(self.font9)

        self.speed_edit = QSpinBox(self)
        self.speed_edit.resize(40, 20)
        self.speed_edit.move(348, 148)
        self.speed_edit.setRange(1, 999)
        self.speed_edit.setToolTip(self.lang_manager.get_string("delay_info"))

        # ++ END DELAY SECTION

        # ++ CONTROLS SECTION

        self.run_btn = QPushButton(self.lang_manager.get_string("launch"), self)
        self.run_btn.resize(167, 25)
        self.run_btn.move(222, 185)
        self.run_btn.setFont(self.font10)
        self.run_btn.setToolTip(self.lang_manager.get_string("launch_info"))

        self.stop_btn = QPushButton(self.lang_manager.get_string("stop"), self)
        self.stop_btn.resize(167, 25)
        self.stop_btn.move(222, 216)
        self.stop_btn.setFont(self.font10)
        self.stop_btn.setToolTip(self.lang_manager.get_string("stop_info"))

        # ++ END CONTROLS SECTION

        # ++ TOKEN INPUT SECTION

        self.token_input = QLineEdit(self)
        self.token_input.resize(378, 20)
        self.token_input.move(10, 252)
        self.token_input.setAlignment(Qt.AlignCenter)
        self.token_input.setToolTip(self.lang_manager.get_string("your_token"))

        # ++ END TOKEN INPUT SECTION

        # + END MAIN SECTION

        self.show()

        self.stop_thread = False
        self.current_info = ""

        self.stop_btn.setEnabled(False)

        self.config_load()

        self.run_btn.clicked.connect(self.run)
        self.stop_btn.clicked.connect(self.stop)
        self.frames_list_edit.doubleClicked.connect(self.edit_frame)
        self.moveUp_frame_btn.clicked.connect(self.moveUp_frame)
        self.moveDown_frame_btn.clicked.connect(self.moveDown_frame)
        self.frames_clear_btn.clicked.connect(self.clear_frames_list)
        self.add_frame_btn.clicked.connect(self.add_frame)
        self.remove_frame_btn.clicked.connect(self.remove_frame)
        self.speed_edit.valueChanged.connect(self.speed_change)
        self.token_input.editingFinished.connect(self.token_editing)

        self.tray_icon.activated.connect(self.tray_click_checking)
        self.tray_icon.messageClicked.connect(self.show)

        self.run_stop_animated_status.triggered.connect(self.run)
        self.exit_the_program.triggered.connect(sys.exit)

        self.custom_signal = custom_signal()
        self.custom_signal.frameUpdated.connect(self.update_frame_screen)
        self.custom_signal.infoUpdated.connect(self.update_info_screen)
        self.custom_signal.threadStopped.connect(self.update_for_stop)

    def run(self):
        """Run animated status."""
        logging.info("Starting animated status...")
        if self.config["frames"] == []:
            self.show()
            logging.error("Failed to run animated status: Frame list is empty.")
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string("error"))
            error.setWindowIcon(self.icon)
            error.setText(self.lang_manager.get_string("frame_list_empty"))
            error.setIcon(error.Warning)
            error.exec_()
        elif self.config["token"] == "":
            self.show()
            logging.error("Failed to run animated status: Token is empty.")
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string("error"))
            error.setWindowIcon(self.icon)
            error.setText(self.lang_manager.get_string("input_token"))
            error.setIcon(error.Warning)
            error.exec_()
            if self.config["hide_token_input"]:
                error = QMessageBox()
                error.setWindowTitle(self.lang_manager.get_string("error"))
                error.setWindowIcon(self.icon)
                error.setText(self.lang_manager.get_string("unhide_token"))
                error.setIcon(error.Warning)
                error.exec_()
        else:
            for char in self.config["token"]:
                if char not in ascii_chars:
                    logging.error("Failed to run animated status: Forbidden chars in token.")
                    error = QMessageBox()
                    error.setWindowTitle(self.lang_manager.get_string("error"))
                    error.setWindowIcon(self.icon)
                    error.setText("В токене обнаружены запрещённые символы.\nУдалите их.") # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    error.setIcon(error.Warning)
                    error.exec_()
                    break
            else:
                self.run_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)

                self.run_stop_animated_status.disconnect()
                self.run_stop_animated_status.setText(self.lang_manager.get_string("stop"))
                self.run_stop_animated_status.triggered.connect(self.stop)

                self.discord_status_updating_thread = Thread(target=self.run_animated_status, daemon=True)
                self.discord_status_updating_thread.start()

                logging.info("Started animated status.")

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
                        if frame["emoji"] == "":
                            self.current_frame = frame["str"]
                        else:
                            self.current_frame = frame["emoji"] + " | " + frame["str"]
                        self.custom_signal.frameUpdated.emit()
                        if self.current_info != "":
                            self.current_info = ""
                            self.custom_signal.infoUpdated.emit()
                    elif req.status_code == 429:  # Never create request overflow
                        logging.error("Discord XRate exceeded. Sleeping for 30s to let Discord rest.")
                        self.current_info = self.lang_manager.get_string("xrate_exceeded")
                        self.custom_signal.infoUpdated.emit()
                        if self.config["tray_notifications"]:
                            self.tray_icon.showMessage("Discord Animated Status", self.lang_manager.get_string("xrate_exceeded"), self.icon, msecs=1000)
                        if self.stop_thread == True:
                            return
                        time.sleep(30)
                except requests.exceptions.RequestException as e:
                    logging.error("A request error occured: %s", e)
                    self.current_info = "%s%s" % (self.lang_manager.get_string("request_error"), e)
                    self.custom_signal.infoUpdated.emit()
                    if self.config["tray_notifications"]:
                        self.tray_icon.showMessage("Discord Animated Status", "%s%s" % (self.lang_manager.get_string("request_error"), e), self.icon, msecs=1000)
                    continue
                if self.stop_thread == True:
                    return
                time.sleep(self.config["delay"])

    def stop(self):
        """Stop animated status."""
        logging.info("Stopping animated status...")
        self.stop_thread = True
        self.stop_btn.setEnabled(False)
        self.run_stop_animated_status.setEnabled(False)
        self.info_screen.setText(self.lang_manager.get_string("stopping"))

        wait_the_stop = Thread(target=self.waiting_the_stop, daemon=True)
        wait_the_stop.start()

    def waiting_the_stop(self):
        self.discord_status_updating_thread.join()

        self.custom_signal.threadStopped.emit()
        self.stop_thread = False

        logging.info("Stopped animated status.")

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
            self.current_info = "%s: %s" % (self.lang_manager.get_string("parse_error"), e)
            self.custom_signal.infoUpdated.emit()

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
            self.current_info = self.lang_manager.get_string("save_error")
            self.custom_signal.infoUpdated.emit()

    def config_load(self):
        """Loads the settings from a config file."""
        try:
            with open("config.json", encoding="utf-8") as cfg_file:
                self.config = json.load(cfg_file)
        except:
            self.config = {"token": "", "frames": [], "delay": 3, "hide_token_input": False, "language": "en"}

        try:
            self.token_input.setText(str(self.config["token"]))
            self.token_input.setToolTip(self.lang_manager.get_string("your_token_tooltip")+str(self.config["token"]))
        except KeyError:
            self.config.update({"token": ""})

        if "frames" not in self.config:
            self.config.update({"frames": []})
        if type(self.config["frames"]) != list:
            self.config["frames"] = []
        self.frames_list_edit_filling()

        try:
            if self.config["delay"] < 1:
                self.config["delay"] = 3
            self.speed_edit.setValue(self.config["delay"])
        except KeyError:
            self.config.update({"delay": 3})
        except:
            self.config["delay"] = 3

        try:
            if self.config["language"] in self.lang_manager.supported_langs:
                self.lang_manager.selected_lang = self.config["language"]
            else:
                self.lang_manager.selected_lang = "en"
        except KeyError:
            self.config.update({"language": "en"})
        except:
            self.config["language"] = "en"

        try:
            if self.config["hide_token_input"] == True:
                self.resize(400, 250)
            else:
                self.resize(400, 280)
        except:
            self.config.update({"hide_token_input": False})
            self.resize(400, 280)

        if "tray_notifications" not in self.config:
            self.config.update({"tray_notifications": True})

        with open("config.json", "w") as cfg_file:
            json.dump(self.config, cfg_file, indent=4)

    def edit_frame(self):
        self.status_edit_window = QDialog()
        self.status_edit_window.setWindowTitle(self.lang_manager.get_string("edit_frame"))
        self.status_edit_window.setWindowIcon(self.icon)
        self.status_edit_window.setMinimumSize(QSize(190, 105))
        self.status_edit_window.setMaximumSize(QSize(190, 105))
        self.status_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        lbl = QLabel(self.lang_manager.get_string("edit_frame_tooltip"), self.status_edit_window)
        lbl.move(10, 15)

        self.emoji_edit = QLineEdit(self.status_edit_window)
        self.emoji_edit.resize(22, 22)
        self.emoji_edit.move(10, 35)
        self.emoji_edit.setMaxLength(1)
        self.emoji_edit.setAlignment(Qt.AlignCenter)
        self.emoji_edit.setPlaceholderText("😉")

        self.text_edit = QLineEdit(self.status_edit_window)
        self.text_edit.resize(140, 22)
        self.text_edit.move(40, 35)
        self.text_edit.setFocus()

        add_btn = QPushButton(self.lang_manager.get_string("add"), self.status_edit_window)
        add_btn.resize(170, 25)
        add_btn.move(10, 71)
        add_btn.setFont(QFont(self.btnFontFamily, 10))

        self.emoji_edit.setText(self.config["frames"][self.frames_list_edit.currentRow()]["emoji"])
        self.text_edit.setText(self.config["frames"][self.frames_list_edit.currentRow()]["str"])

        add_btn.clicked.connect(self.save_frame)
        self.status_edit_window.exec_()

    def save_frame(self):
        text = self.text_edit.text().strip()
        emoji = self.emoji_edit.text().strip()
        self.config["frames"][self.frames_list_edit.currentRow()] = {"str": text, "emoji": emoji}
        if text == "":
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string(self.lang_manager.get_string("error")))
            error.setWindowIcon(self.icon)
            error.setText(self.lang_manager.get_string("input_status"))
            error.setIcon(error.Warning)
            error.exec_()
            self.text_edit.clear()
            return

        if emoji == "":
            new_item = text
        else:
            new_item = emoji+" | "+text

        self.frames_list_edit.currentItem().setText(new_item)
        self.frames_list_edit.row(self.frames_list_edit.currentItem())
        with open("config.json", "w") as cfg_file:
            json.dump(self.config, cfg_file, indent=4)
        self.status_edit_window.close()

    def frames_list_edit_filling(self):
        self.frames_list_edit.clear()
        for frame in self.config["frames"]:
            try:
                if frame["emoji"] == "":
                    new_item = frame["str"]
                else:
                    new_item = frame["emoji"] + " | " + frame["str"]
                self.frames_list_edit.addItem(new_item)
            except:
                del self.config["frames"][self.config["frames"].index(frame)]

    def moveUp_frame(self):
        try:
            currentRow = self.frames_list_edit.currentRow()
            currentItem = self.config["frames"][currentRow]

            if currentRow == 0:
                return

            del self.config["frames"][currentRow]
            self.config["frames"].insert(currentRow - 1, currentItem)

            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(currentRow - 1)

            with open("config.json", "w") as cfg_file:
                json.dump(self.config, cfg_file, indent=4)
        except:
            pass
    
    def moveDown_frame(self):
        try:
            currentRow = self.frames_list_edit.currentRow()
            currentItem = self.config["frames"][currentRow]

            if currentRow == self.frames_list_edit.count() - 1:
                return

            del self.config["frames"][currentRow]
            self.config["frames"].insert(currentRow + 1, currentItem)

            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(currentRow + 1)

            with open("config.json", "w") as cfg_file:
                json.dump(self.config, cfg_file, indent=4)
        except:
            pass

    def clear_frames_list(self):
        """Clear all animated status frames."""
        if self.config["frames"] != []:
            warning=QMessageBox()
            warning.setWindowTitle("Внимание")
            warning.setText("Вы уверены что хотите безвозвратно\nочистить список кадров?") # <<<<<<<<<<<<<<<<<<<<<<<<
            warning.setIcon(warning.Warning)
            warning.setWindowIcon(self.icon)
            warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            yes=warning.button(QMessageBox.Yes)
            yes.setText("Да") # <<<<<<<<<<<<<<<<<<<<<<<
            no=warning.button(QMessageBox.Cancel)
            no.setText("Отмена") # <<<<<<<<<<<<<<<<<<<<<<

            answer=warning.exec()

            if answer==QMessageBox.Yes:
                self.frames_list_edit.clear()
                self.config["frames"] = []
                with open("config.json", "w") as cfg_file:
                    json.dump(self.config, cfg_file, indent=4)

    def add_frame(self):
        self.status_edit_window = QDialog()
        self.status_edit_window.setWindowTitle(self.lang_manager.get_string("new_frame"))
        self.status_edit_window.setWindowIcon(self.icon)
        self.status_edit_window.setMinimumSize(QSize(190, 105))
        self.status_edit_window.setMaximumSize(QSize(190, 105))
        self.status_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        lbl = QLabel(self.lang_manager.get_string("add_frame_tooltip"), self.status_edit_window)
        lbl.move(10, 15)

        self.emoji_edit = QLineEdit(self.status_edit_window)
        self.emoji_edit.resize(22, 22)
        self.emoji_edit.move(10, 35)
        self.emoji_edit.setMaxLength(1)
        self.emoji_edit.setAlignment(Qt.AlignCenter)
        self.emoji_edit.setPlaceholderText("😉")

        self.text_edit = QLineEdit(self.status_edit_window)
        self.text_edit.resize(140, 22)
        self.text_edit.move(40, 35)
        self.text_edit.setFocus()

        lbl = QLabel(self.lang_manager.get_string("regex"), self.status_edit_window)
        lbl.move(10, 40)

        add_btn = QPushButton(self.lang_manager.get_string("add"), self.status_edit_window)
        add_btn.resize(170, 25)
        add_btn.move(10, 71)
        add_btn.setFont(QFont(self.btnFontFamily, 10))

        add_btn.clicked.connect(self.new_frame)
        self.status_edit_window.exec_()

    def about(self):
        self.about_window = QDialog()
        self.about_window.setWindowTitle(self.lang_manager.get_string("about"))
        self.about_window.setWindowIcon(self.icon)
        self.about_window.setMinimumSize(QSize(350, 250))
        self.about_window.setMaximumSize(QSize(350, 250))
        self.about_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.about_window_bg_label = QLabel("", self.about_window)
        self.about_window_bg_label.setAlignment(Qt.AlignCenter)
        self.about_window_bg_label.resize(350, 250)

        y = 0
        for k in authors_m:
            lbl = QLabel(k, self.about_window)
            lbl.setFont(self.font7)
            lbl.setAlignment(Qt.AlignCenter)
            txt_width = lbl.fontMetrics().boundingRect(lbl.text()).width()
            txt_height = lbl.fontMetrics().boundingRect(lbl.text()).height()
            lbl.move(350/2-txt_width/2, 250/2+(txt_height*y)-30)
            y += 1

        self.about_window_version_label = QLabel("Version: %s" % version_m, self.about_window)
        self.about_window_version_label.setFont(self.font10)
        self.about_window_version_label.setAlignment(Qt.AlignCenter)
        txt_width = self.about_window_version_label.fontMetrics().boundingRect(self.about_window_version_label.text()).width()
        self.about_window_version_label.move(350/2-txt_width/2, 250/2+40)

        self.about_window_bg = QMovie("res/about-bg.gif")
        self.about_window_bg_label.setMovie(self.about_window_bg)
        self.about_window_bg.start()

        self.about_window.exec_()

    def new_frame(self):
        text = self.text_edit.text().strip()
        emoji = self.emoji_edit.text().strip()
        self.config["frames"].append({"str": text, "emoji": emoji})
        if text == "":
            logging.error("Failed to add new frame: Text field was empty.")
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string("error"))
            error.setWindowIcon(QIcon("icon.ico"))
            error.setText(self.lang_manager.get_string("input_status"))
            error.setIcon(error.Warning)
            error.exec_()
            self.text_edit.clear()
            return

        if emoji == "":
            new_item = text
        else:
            new_item = emoji+" | "+text

        self.frames_list_edit.addItem(new_item)
        with open("config.json", "w") as cfg_file:
            json.dump(self.config, cfg_file, indent=4)
        self.status_edit_window.close()

    def remove_frame(self):
        try:
            currentRow=self.frames_list_edit.currentRow()
            del self.config["frames"][currentRow]
        
            self.frames_list_edit_filling()

            with open("config.json", "w") as cfg_file:
                json.dump(self.config, cfg_file, indent=4)

            if len(self.config["frames"]) == currentRow:
                currentRow -= 1
            self.frames_list_edit.setCurrentRow(currentRow)
        except:
            logging.error("Failed to remove frame from frame list.")
            pass

    def speed_change(self):
        self.config["delay"] = self.speed_edit.value()
        with open("config.json", "w") as cfg_file:
            json.dump(self.config, cfg_file, indent=4)

    def token_editing(self):
        self.config["token"] = self.token_input.text()
        self.token_input.setToolTip(self.lang_manager.get_string("your_token_tooltip")+self.config["token"])
        with open("config.json", "w") as cfg_file:
            json.dump(self.config, cfg_file, indent=4)

    def resizeEvent(self, event):
        size = (self.size().width(), self.size().height())
        try:
            if size == (400, 280):
                self.config["hide_token_input"] = False
                with open("config.json", "w") as cfg_file:
                    json.dump(self.config, cfg_file, indent=4)
            elif size == (400, 250):
                self.config["hide_token_input"] = True
                with open("config.json", "w") as cfg_file:
                    json.dump(self.config, cfg_file, indent=4)
        except:
            pass

    def update_frame_screen(self):
        self.current_frame_screen.setText(self.current_frame)

    def update_info_screen(self):
        self.info_screen.setText(self.current_info)

    def update_for_stop(self):
        self.run_btn.setEnabled(True)

        self.run_stop_animated_status.setText(self.lang_manager.get_string("launch"))
        self.run_stop_animated_status.setEnabled(True)
        self.run_stop_animated_status.disconnect()
        self.run_stop_animated_status.triggered.connect(self.run)

        self.current_frame_screen.setText("")
        self.info_screen.setText("")

    def changeEvent(self, event):
        if self.windowState() == Qt.WindowMinimized:
            self.hide()

    def tray_click_checking(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.showMaximized()
            
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())

class custom_signal(QObject):
    """Custom PyQT signal class."""
    frameUpdated = pyqtSignal()
    infoUpdated = pyqtSignal()
    threadStopped = pyqtSignal()

def apply_style(app):
    """Apply dark discord theme to application."""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(54, 57, 63))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(47, 50, 55))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(74, 103, 207))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor(80, 93, 136))
    app.setPalette(palette)
