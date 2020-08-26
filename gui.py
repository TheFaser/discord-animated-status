from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from required import logging, sys, os, Thread, ascii_chars, authors_m, version_m
from core import Core
from lang import LanguageManager

class App(QWidget):
    """Main application class."""

    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.core = Core(self)
        self.mainWindow()

    def restart(self):
        """Restarts the program."""
        logging.info("Forced restart. Restarting...")
        self.core.config_save()
        self.tray_icon.hide()
        scr = sys.executable
        os.execl(scr, scr, *sys.argv)

    def make_lang_callback(self, lang):
        """Method factory for menu bar language selection."""
        def execute_choice(choice):
            if choice == "restart":
                self.lang_manager.selected_lang = lang
                self.core.config["language"] = self.lang_manager.selected_lang
                self.restart()
            elif choice == "later":
                self.core.config["language"] = lang
                self.core.config_save()
                self.language_change_confirm_window.close()
        
        def f():
            self.language_change_confirm_window = QDialog()
            self.language_change_confirm_window.setWindowTitle(self.lang_manager.get_string("language"))
            self.language_change_confirm_window.setWindowIcon(self.icon)
            self.language_change_confirm_window.setMinimumSize(QSize(190, 90))
            self.language_change_confirm_window.setMaximumSize(QSize(190, 90))
            self.language_change_confirm_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

            lbl = QLabel(self.lang_manager.get_string("restart_for_language_change"), self.language_change_confirm_window)
            lbl.move(10, 10)

            restart_btn = QPushButton(self.lang_manager.get_string("restart"), self.language_change_confirm_window)
            restart_btn.resize(100, 25)
            restart_btn.move(10, 55)
            restart_btn.setFont(QFont(self.btnFontFamily, 10))

            later_btn = QPushButton(self.lang_manager.get_string("later"), self.language_change_confirm_window)
            later_btn.resize(65, 25)
            later_btn.move(115, 55)
            later_btn.setFont(QFont(self.btnFontFamily, 10))

            restart_btn.clicked.connect(lambda: execute_choice("restart"))
            later_btn.clicked.connect(lambda: execute_choice("later"))
            
            self.language_change_confirm_window.exec_()
        
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
        self.menu_bar_config_load.triggered.connect(self.core.config_load)
        self.menu_bar_config_save = QAction(self.lang_manager.get_string("save"), self)
        self.menu_bar_config_save.triggered.connect(self.core.config_save)
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
        lbl.resize(167, 20)
        lbl.move(222, 13)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(self.font9)

        self.current_frame_screen = QTextBrowser(self)
        self.current_frame_screen.resize(167, 40)
        self.current_frame_screen.move(222, 32)
        self.current_frame_screen.setFont(self.font8)
        self.current_frame_screen.setToolTip(self.lang_manager.get_string("current_displayed_frame"))

        # ++ END CURRENT FRAME SECTION

        # ++ INFO SECTION

        lbl = QLabel(self.lang_manager.get_string("info"), self)
        lbl.resize(167, 20)
        lbl.move(222, 73)
        lbl.setAlignment(Qt.AlignCenter)
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
        self.token_input.setPlaceholderText(self.lang_manager.get_string("your_token"))
        self.token_input.setToolTip(self.lang_manager.get_string("your_token"))

        # ++ END TOKEN INPUT SECTION

        # + END MAIN SECTION

        self.show()

        self.core.stop_thread = False
        self.current_info = ""

        self.stop_btn.setEnabled(False)

        self.core.config_load()

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
        self.exit_the_program.triggered.connect(self.close_app)

        self.custom_signal = custom_signal()
        self.custom_signal.frameUpdated.connect(self.update_frame_screen)
        self.custom_signal.infoUpdated.connect(self.update_info_screen)
        self.custom_signal.threadStopped.connect(self.update_for_stop)

    def run(self):
        """Run animated status."""
        logging.info("Starting animated status...")
        if self.core.config["frames"] == []:
            self.show()
            logging.error("Failed to run animated status: Frame list is empty.")
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string("error"))
            error.setWindowIcon(self.icon)
            error.setText(self.lang_manager.get_string("frame_list_empty"))
            error.setIcon(error.Warning)
            error.exec_()
        elif self.core.config["token"] == "":
            self.show()
            logging.error("Failed to run animated status: Token is empty.")
            error = QMessageBox()
            error.setWindowTitle(self.lang_manager.get_string("error"))
            error.setWindowIcon(self.icon)
            error.setText(self.lang_manager.get_string("input_token"))
            error.setIcon(error.Warning)
            error.exec_()
            if self.core.config["hide_token_input"]:
                error = QMessageBox()
                error.setWindowTitle(self.lang_manager.get_string("error"))
                error.setWindowIcon(self.icon)
                error.setText(self.lang_manager.get_string("unhide_token"))
                error.setIcon(error.Warning)
                error.exec_()
        else:
            for char in self.core.config["token"]:
                if char not in ascii_chars:
                    logging.error("Failed to run animated status: Forbidden chars in token.")
                    error = QMessageBox()
                    error.setWindowTitle(self.lang_manager.get_string("error"))
                    error.setWindowIcon(self.icon)
                    error.setText(self.lang_manager.get_string("token_invalid"))
                    error.setIcon(error.Warning)
                    error.exec_()
                    break
            else:
                self.run_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)

                self.run_stop_animated_status.disconnect()
                self.run_stop_animated_status.setText(self.lang_manager.get_string("stop"))
                self.run_stop_animated_status.triggered.connect(self.stop)

                self.discord_status_updating_thread = Thread(target=self.core.run_animated_status, daemon=True)
                self.discord_status_updating_thread.start()

                logging.info("Started animated status.")

    def stop(self):
        """Stop animated status."""
        logging.info("Stopping animated status...")
        self.core.stop_thread = True
        self.stop_btn.setEnabled(False)
        self.run_stop_animated_status.setEnabled(False)
        self.info_screen.setText(self.lang_manager.get_string("stopping"))

        wait_the_stop = Thread(target=self.waiting_the_stop, daemon=True)
        wait_the_stop.start()

    def waiting_the_stop(self):
        self.discord_status_updating_thread.join()

        self.custom_signal.threadStopped.emit()
        self.core.stop_thread = False

        logging.info("Stopped animated status.")

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

        self.emoji_edit.setText(self.core.config["frames"][self.frames_list_edit.currentRow()]["emoji"])
        self.text_edit.setText(self.core.config["frames"][self.frames_list_edit.currentRow()]["str"])

        add_btn.clicked.connect(self.save_frame)
        self.status_edit_window.exec_()

    def save_frame(self):
        text = self.text_edit.text().strip()
        emoji = self.emoji_edit.text().strip()
        self.core.config["frames"][self.frames_list_edit.currentRow()] = {"str": text, "emoji": emoji}
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
        self.core.config_save()
        self.status_edit_window.close()

    def frames_list_edit_filling(self):
        self.frames_list_edit.clear()
        for frame in self.core.config["frames"]:
            try:
                if frame["emoji"] == "":
                    new_item = frame["str"]
                else:
                    new_item = frame["emoji"] + " | " + frame["str"]
                self.frames_list_edit.addItem(new_item)
            except:
                del self.core.config["frames"][self.core.config["frames"].index(frame)]

    def moveUp_frame(self):
        try:
            currentRow = self.frames_list_edit.currentRow()
            currentItem = self.core.config["frames"][currentRow]

            if currentRow == 0:
                return

            del self.core.config["frames"][currentRow]
            self.core.config["frames"].insert(currentRow - 1, currentItem)

            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(currentRow - 1)

            self.core.config_save()
        except:
            pass
    
    def moveDown_frame(self):
        try:
            currentRow = self.frames_list_edit.currentRow()
            currentItem = self.core.config["frames"][currentRow]

            if currentRow == self.frames_list_edit.count() - 1:
                return

            del self.core.config["frames"][currentRow]
            self.core.config["frames"].insert(currentRow + 1, currentItem)

            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(currentRow + 1)

            self.core.config_save()
        except:
            pass

    def clear_frames_list(self):
        """Clear all animated status frames."""
        if self.core.config["frames"] != []:
            warning=QMessageBox()
            warning.setWindowTitle(self.lang_manager.get_string("warning"))
            warning.setText(self.lang_manager.get_string("clear_warning"))
            warning.setIcon(warning.Warning)
            warning.setWindowIcon(self.icon)
            warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            yes=warning.button(QMessageBox.Yes)
            yes.setText(self.lang_manager.get_string("yes"))
            no=warning.button(QMessageBox.Cancel)
            no.setText(self.lang_manager.get_string("cancel"))

            answer=warning.exec()

            if answer==QMessageBox.Yes:
                self.frames_list_edit.clear()
                self.core.config["frames"] = []
                self.core.config_save()

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
        self.core.config["frames"].append({"str": text, "emoji": emoji})
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
        self.core.config_save()
        self.status_edit_window.close()

    def remove_frame(self):
        try:
            currentRow=self.frames_list_edit.currentRow()
            del self.core.config["frames"][currentRow]
        
            self.frames_list_edit_filling()

            self.core.config_save()

            if len(self.core.config["frames"]) == currentRow:
                currentRow -= 1
            self.frames_list_edit.setCurrentRow(currentRow)
        except:
            logging.error("Failed to remove frame from frame list.")
            pass

    def speed_change(self):
        self.core.config["delay"] = self.speed_edit.value()
        self.core.config_save()

    def token_editing(self):
        self.core.config["token"] = self.token_input.text()
        self.token_input.setToolTip(self.lang_manager.get_string("your_token_tooltip")+self.core.config["token"])
        self.core.config_save()

    def resizeEvent(self, event):
        size = (self.size().width(), self.size().height())
        try:
            if size == (400, 280):
                self.core.config["hide_token_input"] = False
                self.core.config_save()
            elif size == (400, 250):
                self.core.config["hide_token_input"] = True
                self.core.config_save()
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

    def close_app(self):
        self.tray_icon.hide()
        sys.exit()

    def closeEvent(self, event):
        self.tray_icon.hide()

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
