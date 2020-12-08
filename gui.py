import sys
import os
import logging
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

if sys.platform == 'win32':
    import winshell
else:
    winshell = None

from constants import ASCII_CHARS, AUTHORS_M, VERSION_M

from core import Core
from lang import LanguageManager

RESOURCES_DIR = {
    'fonts': ['uni_sans_heavy.ttf', 'whitney_bold.ttf', 'whitney_medium.ttf'],
    'images': ['about-bg.gif'],
    'files': ['icon.ico', 'lang.json'],
}

PROXY_EXAMPLES = '''
ip:port
http://ip:port
http://user:pass@ip:port
https://ip:port
https://user:pass@ip:port
socks4://ip:port
socks4://user:pass@ip:port
socks5://ip:port
socks5://user:pass@ip:port
'''

class App(QWidget):
    """Main application class."""

    frameUpdated = pyqtSignal()
    infoUpdated = pyqtSignal()
    authFailed = pyqtSignal()

    def __init__(self, launch_args):
        super().__init__()
        self.core = Core(self)
        self.lang_manager = LanguageManager()
        self.init_gui(launch_args)

    def restart(self):
        """Restarts the program."""
        logging.info("Forced restart. Restarting...")
        self.tray_icon.hide()
        if self.core.rpc:
            try:
                if self.core.rpc.loop.is_running():
                    self.core.rpc.loop.stop()
                else:
                    self.core.rpc.close()
            except Exception as error:
                logging.error('Failed to close RPC: %s', repr(error))
        scr = sys.executable
        os.execl(scr, '"%s"' % scr, *sys.argv)

    def make_lang_callback(self, lang):
        """Method factory for menu bar language selection."""
        def execute_choice(choice):
            if choice == "restart":
                self.lang_manager.selected_lang = lang
                self.core.config["language"] = self.lang_manager.selected_lang
                self.core.config_save()
                logging.info('Selected language saved.')
                self.restart()
            elif choice == "later":
                self.core.config["language"] = lang
                self.core.config_save()
                logging.info('Selected language saved.')
                self.language_change_confirm_window.close()

        def confirm_lang_change():
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
            self.language_change_confirm_window.deleteLater()
        
        return confirm_lang_change

    def init_gui(self, launch_args):
        """Initialize application layout."""
        self.setMinimumSize(QSize(400, 250))
        self.setMaximumSize(QSize(400, 250))

        self.core.config_load()
        self.core.load_statistics()

        self.lang_manager.load_language(self.core.config['language'])

        # + PRESETS SECTION

        font_db = QFontDatabase()
        uni_sans_heavy_id = font_db.addApplicationFont('res/fonts/uni_sans_heavy.ttf')
        whitney_bold_id = font_db.addApplicationFont('res/fonts/whitney_bold.ttf')
        whitney_medium_id = font_db.addApplicationFont('res/fonts/whitney_medium.ttf')
        self.btnFontFamily = font_db.applicationFontFamilies(uni_sans_heavy_id)[0]
        self.whitney_bold = font_db.applicationFontFamilies(whitney_bold_id)[0]
        self.whitney_medium = font_db.applicationFontFamilies(whitney_medium_id)[0]

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

        self.whitney_bold_9 = QFont()
        self.whitney_bold_9.setFamily(self.whitney_bold)
        self.whitney_bold_9.setPointSize(9)

        self.whitney_medium_10 = QFont()
        self.whitney_medium_10.setFamily(self.whitney_medium)
        self.whitney_medium_10.setPointSize(10)

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

        self.menu_bar_settings = self.menu_bar.addMenu(self.lang_manager.get_string("config"))
        self.menu_bar_settings_token = QAction(self.lang_manager.get_string("token"), self)
        self.menu_bar_settings_token.triggered.connect(self.edit_token)
        self.menu_bar_settings_load = QAction(self.lang_manager.get_string("load_config"), self)
        self.menu_bar_settings_load.triggered.connect(self.reload_config)
        self.menu_bar_settings_save = QAction(self.lang_manager.get_string("save_config"), self)
        self.menu_bar_settings_save.triggered.connect(self.core.config_save)
        self.menu_bar_settings_autostart_on_boot = QAction(self.lang_manager.get_string("autostart_on_boot"), self)
        self.menu_bar_settings_autostart_on_boot.triggered.connect(self.autostart_on_boot)
        self.menu_bar_settings_proxy = QAction(self.lang_manager.get_string("proxy"), self)
        self.menu_bar_settings_proxy.triggered.connect(self.edit_proxy)
        self.menu_bar_settings_discord_rpc = QAction("Discord RPC", self)
        self.menu_bar_settings_discord_rpc.triggered.connect(self.default_discord_rpc_edit)
        self.menu_bar_settings.addAction(self.menu_bar_settings_token)
        self.menu_bar_settings.addAction(self.menu_bar_settings_save)
        self.menu_bar_settings.addAction(self.menu_bar_settings_load)
        self.menu_bar_settings.addAction(self.menu_bar_settings_autostart_on_boot)
        self.menu_bar_settings.addAction(self.menu_bar_settings_proxy)
        self.menu_bar_settings.addAction(self.menu_bar_settings_discord_rpc)

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
        lbl.move(224, 140)
        lbl.setFont(self.font9)

        self.speed_edit = QSpinBox(self)
        self.speed_edit.resize(40, 20)
        self.speed_edit.move(348, 138)
        self.speed_edit.setRange(1, 999)
        self.speed_edit.setToolTip(self.lang_manager.get_string("delay_info"))

        # ++ END DELAY SECTION

        # ++ CONTROLS SECTION

        self.randomize_frames_checkbox = QCheckBox(self.lang_manager.get_string('randomize_frames'), self)
        self.randomize_frames_checkbox.move(224, 157)
        self.randomize_frames_checkbox.setFont(self.font9)

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

        # + END MAIN SECTION

        self.current_info = ""

        self.stop_btn.setEnabled(False)
        self.setFocus()

        self.run_btn.clicked.connect(self.run_animation)
        self.stop_btn.clicked.connect(self.stop_animation)
        self.frames_list_edit.doubleClicked.connect(self.edit_frame)
        self.moveUp_frame_btn.clicked.connect(self.moveUp_frame)
        self.moveDown_frame_btn.clicked.connect(self.moveDown_frame)
        self.frames_clear_btn.clicked.connect(self.clear_frames_list)
        self.add_frame_btn.clicked.connect(self.add_frame)
        self.remove_frame_btn.clicked.connect(self.remove_frame)
        self.speed_edit.editingFinished.connect(self.speed_change)
        self.randomize_frames_checkbox.stateChanged.connect(self.switch_frames_randomizing)

        self.tray_icon.activated.connect(self.tray_click_checking)
        self.tray_icon.messageClicked.connect(self.maximize_window)

        self.run_stop_animated_status.triggered.connect(self.run_animation)
        self.exit_the_program.triggered.connect(self.close)

        self.frameUpdated.connect(self.update_frame_screen)
        self.infoUpdated.connect(self.update_info_screen)
        self.authFailed.connect(self.on_auth_failed)

        self.core.apply_config()

        if not launch_args.minimize:
            self.show()
        else:
            logging.info('Program window minimized by launch argument.')

        if launch_args.run_animation:
            self.run_animation(silent=True)

        logging.info('GUI initialized.')

    def run_animation(self, silent=False):
        """Run animated status."""
        logging.info("Starting animated status...")
        if self.core.config["frames"] == []:
            logging.error("Failed to run animated status: Frame list is empty.")
            if not silent:
                if self.isHidden():
                    self.maximize_window()
                warning_window = QMessageBox()
                warning_window.setWindowTitle(self.lang_manager.get_string("error"))
                warning_window.setWindowIcon(self.icon)
                warning_window.setText(self.lang_manager.get_string("frame_list_empty"))
                warning_window.setIcon(warning_window.Warning)
                warning_window.exec_()
                warning_window.deleteLater()
        elif self.core.config["token"] == "":
            logging.error("Failed to run animated status: Token is empty.")
            if not silent:
                if self.isHidden():
                    self.maximize_window()
                warning_window = QMessageBox()
                warning_window.setWindowTitle(self.lang_manager.get_string("error"))
                warning_window.setWindowIcon(self.icon)
                warning_window.setText(self.lang_manager.get_string("input_token"))
                warning_window.setIcon(warning_window.Warning)
                warning_window.exec_()
                warning_window.deleteLater()
        else:
            for char in self.core.config["token"]:
                if char not in ASCII_CHARS:
                    logging.error("Failed to run animated status: Forbidden chars in token.")
                    if not silent:
                        self.maximize_window()
                        warning_window = QMessageBox()
                        warning_window.setWindowTitle(self.lang_manager.get_string("error"))
                        warning_window.setWindowIcon(self.icon)
                        warning_window.setText(self.lang_manager.get_string("token_invalid"))
                        warning_window.setIcon(warning_window.Warning)
                        warning_window.exec_()
                        warning_window.deleteLater()
                    break
            else:
                self.run_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)

                self.run_stop_animated_status.disconnect()
                self.run_stop_animated_status.setText(self.lang_manager.get_string("stop"))
                self.run_stop_animated_status.triggered.connect(self.stop_animation)

                self.core.requests_thread.start()

                logging.info("Started animated status.")

    def stop_animation(self):
        """Stop animated status."""
        logging.info("Stopping animated status...")
        self.stop_btn.setEnabled(False)
        self.run_stop_animated_status.setEnabled(False)
        self.info_screen.setText(self.lang_manager.get_string("stopping"))

        self.core.requests_thread.terminate()

        logging.info("Stopped animated status.")

    def frames_list_edit_filling(self):
        logging.info('Frames list filling...')
        self.frames_list_edit.clear()
        for frame_id, frame in enumerate(self.core.config["frames"].copy()):
            try:
                frame = frame.copy()
                if frame.get('custom_emoji_id'):
                    frame['custom_emoji_id'] = 'C'
                    frame['emoji'] = ''
                if ''.join(list(frame.get('rpc', {}).values())):
                    frame['rpc'] = 'RPC'

                new_item = ' | '.join([e for e in reversed(list(frame.values())) if e])
                self.frames_list_edit.addItem(new_item)

            except Exception as error:
                logging.error("Failed to add frame #%s while filling: %s", frame_id, repr(error))

        logging.info('Frames list has been filled.')

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

            logging.info('Frame #%s has been moved up.', currentRow)

        except Exception as error:
            logging.error('Failed to move up frame: %s', repr(error))
    
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

            logging.info('Frame #%s has been moved down.', currentRow)

        except Exception as error:
            logging.error('Failed to move down frame: %s', repr(error))

    def clear_frames_list(self):
        """Clear all animated status frames."""
        if self.core.config["frames"] != []:
            warning_window = QMessageBox()
            warning_window.setWindowTitle(self.lang_manager.get_string("warning"))
            warning_window.setText(self.lang_manager.get_string("clear_warning"))
            warning_window.setIcon(warning_window.Warning)
            warning_window.setWindowIcon(self.icon)
            warning_window.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            yes = warning_window.button(QMessageBox.Yes)
            yes.setText(self.lang_manager.get_string("yes"))
            no = warning_window.button(QMessageBox.Cancel)
            no.setText(self.lang_manager.get_string("cancel"))

            answer = warning_window.exec()
            warning_window.deleteLater()

            if answer == QMessageBox.Yes:
                self.frames_list_edit.clear()
                self.core.config["frames"] = []
                self.core.config_save()

                logging.info('Frame list has been cleared.')

    def remove_frame(self):
        try:
            currentRow = self.frames_list_edit.currentRow()
            del self.core.config["frames"][currentRow]

            self.frames_list_edit_filling()
            self.core.config_save()

            logging.info('Frame #%s has been removed.', currentRow)

            if len(self.core.config["frames"]) == currentRow:
                currentRow -= 1
            self.frames_list_edit.setCurrentRow(currentRow)

        except Exception as error:
            logging.error("Failed to remove frame from frame list: %s", repr(error))

    def edit_token(self):
        token_edit_window = QDialog()
        token_edit_window.setWindowTitle(self.lang_manager.get_string("token"))
        token_edit_window.setWindowIcon(self.icon)
        token_edit_window.setMinimumSize(QSize(375, 105))
        token_edit_window.setMaximumSize(QSize(375, 105))
        token_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        token_edit_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        lbl = QLabel(self.lang_manager.get_string('your_token'), token_edit_window)
        lbl.move(20, 15)

        token_edit = QLineEdit(token_edit_window)
        token_edit.resize(335, 22)
        token_edit.move(20, 35)

        save_btn = QPushButton(self.lang_manager.get_string("save"), token_edit_window)
        save_btn.resize(125, 25)
        save_btn.move(20, 68)
        save_btn.setFont(QFont(self.btnFontFamily, 10))
        save_btn.setFocusPolicy(Qt.NoFocus)

        hide_token_checkbox = QCheckBox(self.lang_manager.get_string('hide'), token_edit_window)
        hide_token_checkbox.resize(150, 25)
        hide_token_checkbox.move(200, 70)
        hide_token_checkbox.setFont(QFont(self.btnFontFamily, 10))
        hide_token_checkbox.setLayoutDirection(Qt.RightToLeft)
        hide_token_checkbox.setFocusPolicy(Qt.NoFocus)
        hide_token_checkbox.toggle()

        self._token_buffer = self.core.config['token']
        self._last_buffer_len = len(self.core.config['token'])
        self._token_is_hide = True

        def save_token():
            if self._token_buffer.strip() == "":
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("enter_the_token"))
                error_window.setIcon(error_window.Warning)
                error_window.exec_()
                error_window.deleteLater()
                token_edit.clear()
                return

            logging.info('Token has been edited.')

            self.core.config["token"] = self._token_buffer
            self.core.config_save()

            token_edit_window.close()

        def switch_token_visibility():
            self._token_is_hide = not self._token_is_hide # switch

            if self._token_is_hide:
                token_edit.setText('*' * len(self._token_buffer))
            else:
                token_edit.setText(self._token_buffer)

        def on_token_edit():
            if self._token_is_hide:
                if len(token_edit.text()) == 0:
                    self._token_buffer = ''
                elif self._last_buffer_len > len(token_edit.text()):
                    min_len = self._last_buffer_len - len(token_edit.text())
                    self._token_buffer = self._token_buffer[:-min_len]
                else:
                    self._token_buffer += token_edit.text()[self._last_buffer_len:]
                self._last_buffer_len = len(token_edit.text())
                token_edit.setText('*' * self._last_buffer_len)

            else:
                self._token_buffer = token_edit.text()

        token_edit.textEdited.connect(on_token_edit)
        hide_token_checkbox.stateChanged.connect(switch_token_visibility)
        save_btn.clicked.connect(save_token)

        token_edit.setText('*' * self._last_buffer_len)

        token_edit_window.setFocus()
        token_edit_window.exec_()
        token_edit_window.deleteLater()

    def add_frame(self):
        frame_edit_window = QDialog()
        frame_edit_window.setWindowTitle(self.lang_manager.get_string("new_frame"))
        frame_edit_window.setWindowIcon(self.icon)
        frame_edit_window.setMinimumSize(QSize(190, 105))
        frame_edit_window.setMaximumSize(QSize(190, 105))
        frame_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        frame_edit_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        emoji_edit = QLineEdit(frame_edit_window)
        emoji_edit.resize(22, 22)
        emoji_edit.move(10, 35)
        emoji_edit.setAlignment(Qt.AlignCenter)
        emoji_edit.setPlaceholderText("😉")
        emoji_edit.setToolTip(self.lang_manager.get_string("status_emoji"))

        text_edit = QLineEdit(frame_edit_window)
        text_edit.resize(140, 22)
        text_edit.move(40, 35)

        add_btn = QPushButton(self.lang_manager.get_string("add"), frame_edit_window)
        add_btn.resize(170, 25)
        add_btn.move(10, 71)
        add_btn.setFont(QFont(self.btnFontFamily, 10))

        def set_rpc():
            if self.core.config['disable_rpc']:
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("rpc_disabled_warning"))
                error_window.setIcon(error_window.Warning)
                error_window.exec_()

            rpc_edit_window, state_edit, details_edit, start_timestamp_edit, end_timestamp_edit, large_image_key_edit, \
            large_image_text_edit, small_image_key_edit, small_image_text_edit = self.get_discord_rpc_window(490, 260)

            def save_rpc():
                self._rpc_buffer['state'] = state_edit.text().strip()
                self._rpc_buffer['details'] = details_edit.text().strip()
                self._rpc_buffer['start_timestamp'] = start_timestamp_edit.text().strip()
                self._rpc_buffer['end_timestamp'] = end_timestamp_edit.text().strip()
                self._rpc_buffer['large_image_key'] = large_image_key_edit.text().strip()
                self._rpc_buffer['large_image_text'] = large_image_text_edit.text().strip()
                self._rpc_buffer['small_image_key'] = small_image_key_edit.text().strip()
                self._rpc_buffer['small_image_text'] = small_image_text_edit.text().strip()

                rpc_edit_window.close()

            set_btn = QPushButton(self.lang_manager.get_string('set'), rpc_edit_window)
            set_btn.resize(110, 25)
            set_btn.move(15, 220)
            set_btn.setFont(QFont(self.btnFontFamily, 10))

            state_edit.setText(str(self._rpc_buffer['state']))
            details_edit.setText(str(self._rpc_buffer['details']))
            start_timestamp_edit.setText(str(self._rpc_buffer['start_timestamp']))
            end_timestamp_edit.setText(str(self._rpc_buffer['end_timestamp']))
            large_image_key_edit.setText(str(self._rpc_buffer['large_image_key']))
            large_image_text_edit.setText(str(self._rpc_buffer['large_image_text']))
            small_image_key_edit.setText(str(self._rpc_buffer['small_image_key']))
            small_image_text_edit.setText(str(self._rpc_buffer['small_image_text']))

            set_btn.clicked.connect(save_rpc)

            rpc_edit_window.setFocus()
            rpc_edit_window.exec_()
            rpc_edit_window.deleteLater()

        def set_custom_emoji():
            custom_emoji_window = QDialog()
            custom_emoji_window.setWindowTitle(self.lang_manager.get_string("custom_emoji"))
            custom_emoji_window.setWindowIcon(self.icon)
            custom_emoji_window.setMinimumSize(QSize(350, 70))
            custom_emoji_window.setMaximumSize(QSize(350, 70))
            custom_emoji_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            custom_emoji_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

            emoji_id_edit = QLineEdit(custom_emoji_window)
            emoji_id_edit.resize(155, 22)
            emoji_id_edit.move(10, 8)
            emoji_id_edit.setPlaceholderText("ID")
            emoji_id_edit.setToolTip(self.lang_manager.get_string("custom_emoji_id_tooltip"))

            nitro_lbl = QLabel(self.lang_manager.get_string('nitro_warning'), custom_emoji_window)
            nitro_lbl.setAlignment(Qt.AlignCenter)
            nitro_lbl.resize(175, 22)
            nitro_lbl.move(170, 20)

            set_btn = QPushButton(self.lang_manager.get_string("set"), custom_emoji_window)
            set_btn.resize(155, 25)
            set_btn.move(10, 37)
            set_btn.setFont(QFont(self.btnFontFamily, 10))

            def save_custom_emoji():
                emoji_id = emoji_id_edit.text().strip()
                if emoji_id and not emoji_id.isdigit():
                    logging.error("Failed to set custom emoji: ID is not a digit.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("invalid_emoji_id"))
                    error_window.setIcon(error_window.Warning)
                    error_window.exec_()
                    return

                if emoji_id:
                    self._custom_emoji_id_buffer = emoji_id_edit.text().strip()
                    emoji_edit.setReadOnly(True)
                    emoji_edit.setText('C')
                else:
                    self._custom_emoji_id_buffer = ''
                    emoji_edit.setReadOnly(False)
                    if emoji_edit.text() == 'C':
                        emoji_edit.setText(self._emoji_buffer)

                custom_emoji_window.close()

            emoji_id_edit.setText(self._custom_emoji_id_buffer)

            set_btn.clicked.connect(save_custom_emoji)

            custom_emoji_window.setFocus()
            custom_emoji_window.exec_()
            custom_emoji_window.deleteLater()

        def on_emoji_edit():
            try:
                e_buffer = emoji_edit.text()[:1].encode('utf-8').decode('utf-8')
                self._emoji_buffer = e_buffer
                emoji_edit.setText(e_buffer)
            except (UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError) as error:
                logging.info('An error has occurred while emoji entering: %s', repr(error))
                self._emoji_buffer = ''
                emoji_edit.setText('')

        def save_new_frame():
            text = text_edit.text().strip()

            if not text:
                if self._emoji_buffer or self._custom_emoji_id_buffer or ''.join(list(self._rpc_buffer.values())):
                    pass
                else:
                    logging.error("Failed to add new frame: Every field is empty.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("input_status"))
                    error_window.setIcon(error_window.Warning)
                    error_window.exec_()
                    error_window.deleteLater()
                    text_edit.clear()
                    return

            new_frame = {"str": text, "emoji": self._emoji_buffer}
            new_frame['custom_emoji_id'] = int(self._custom_emoji_id_buffer) if self._custom_emoji_id_buffer else ''
            if ''.join(list(self._rpc_buffer.values())):
                new_frame['rpc'] = self._rpc_buffer

            self.core.config["frames"].append(new_frame)

            logging.info('New frame has been added.')

            self.core.config_save()
            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(self.frames_list_edit.count() - 1)
            frame_edit_window.close()

        menu_bar = QMenuBar(frame_edit_window)
        menu_bar.setFont(self.font9)
        menu_bar_more = menu_bar.addMenu(self.lang_manager.get_string("more"))
        menu_bar_custom_emoji = QAction(self.lang_manager.get_string("custom_emoji"), frame_edit_window)
        menu_bar_custom_emoji.triggered.connect(set_custom_emoji)
        menu_bar_rpc = QAction('RPC', frame_edit_window)
        menu_bar_rpc.triggered.connect(set_rpc)
        menu_bar_more.addAction(menu_bar_custom_emoji)
        menu_bar_more.addAction(menu_bar_rpc)

        add_btn.clicked.connect(save_new_frame)
        emoji_edit.textEdited.connect(on_emoji_edit)

        self._emoji_buffer = ''
        self._custom_emoji_id_buffer = ''
        self._rpc_buffer = {}
        self._rpc_buffer['state'] = ''
        self._rpc_buffer['details'] = ''
        self._rpc_buffer['start_timestamp'] = ''
        self._rpc_buffer['end_timestamp'] = ''
        self._rpc_buffer['large_image_key'] = ''
        self._rpc_buffer['large_image_text'] = ''
        self._rpc_buffer['small_image_key'] = ''
        self._rpc_buffer['small_image_text'] = ''

        frame_edit_window.setFocus()
        frame_edit_window.exec_()
        frame_edit_window.deleteLater()

    def edit_frame(self):
        frame_edit_window = QDialog()
        frame_edit_window.setWindowTitle(self.lang_manager.get_string("new_frame"))
        frame_edit_window.setWindowIcon(self.icon)
        frame_edit_window.setMinimumSize(QSize(190, 105))
        frame_edit_window.setMaximumSize(QSize(190, 105))
        frame_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        frame_edit_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        emoji_edit = QLineEdit(frame_edit_window)
        emoji_edit.resize(22, 22)
        emoji_edit.move(10, 35)
        emoji_edit.setAlignment(Qt.AlignCenter)
        emoji_edit.setPlaceholderText("😉")
        emoji_edit.setToolTip(self.lang_manager.get_string("status_emoji"))

        text_edit = QLineEdit(frame_edit_window)
        text_edit.resize(140, 22)
        text_edit.move(40, 35)

        add_btn = QPushButton(self.lang_manager.get_string("save"), frame_edit_window)
        add_btn.resize(170, 25)
        add_btn.move(10, 71)
        add_btn.setFont(QFont(self.btnFontFamily, 10))

        def set_rpc():
            if self.core.config['disable_rpc']:
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("rpc_disabled_warning"))
                error_window.setIcon(error_window.Warning)
                error_window.exec_()

            rpc_edit_window, state_edit, details_edit, start_timestamp_edit, end_timestamp_edit, large_image_key_edit, \
            large_image_text_edit, small_image_key_edit, small_image_text_edit = self.get_discord_rpc_window(490, 260)

            def save_rpc():
                self._rpc_buffer['state'] = state_edit.text().strip()
                self._rpc_buffer['details'] = details_edit.text().strip()
                self._rpc_buffer['start_timestamp'] = start_timestamp_edit.text().strip()
                self._rpc_buffer['end_timestamp'] = end_timestamp_edit.text().strip()
                self._rpc_buffer['large_image_key'] = large_image_key_edit.text().strip()
                self._rpc_buffer['large_image_text'] = large_image_text_edit.text().strip()
                self._rpc_buffer['small_image_key'] = small_image_key_edit.text().strip()
                self._rpc_buffer['small_image_text'] = small_image_text_edit.text().strip()

                rpc_edit_window.close()

            set_btn = QPushButton(self.lang_manager.get_string('set'), rpc_edit_window)
            set_btn.resize(110, 25)
            set_btn.move(15, 220)
            set_btn.setFont(QFont(self.btnFontFamily, 10))

            state_edit.setText(str(self._rpc_buffer['state']))
            details_edit.setText(str(self._rpc_buffer['details']))
            start_timestamp_edit.setText(str(self._rpc_buffer['start_timestamp']))
            end_timestamp_edit.setText(str(self._rpc_buffer['end_timestamp']))
            large_image_key_edit.setText(str(self._rpc_buffer['large_image_key']))
            large_image_text_edit.setText(str(self._rpc_buffer['large_image_text']))
            small_image_key_edit.setText(str(self._rpc_buffer['small_image_key']))
            small_image_text_edit.setText(str(self._rpc_buffer['small_image_text']))

            set_btn.clicked.connect(save_rpc)

            rpc_edit_window.setFocus()
            rpc_edit_window.exec_()

        def set_custom_emoji():
            custom_emoji_window = QDialog()
            custom_emoji_window.setWindowTitle(self.lang_manager.get_string("custom_emoji"))
            custom_emoji_window.setWindowIcon(self.icon)
            custom_emoji_window.setMinimumSize(QSize(350, 70))
            custom_emoji_window.setMaximumSize(QSize(350, 70))
            custom_emoji_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            custom_emoji_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

            emoji_id_edit = QLineEdit(custom_emoji_window)
            emoji_id_edit.resize(155, 22)
            emoji_id_edit.move(10, 8)
            emoji_id_edit.setPlaceholderText("ID")
            emoji_id_edit.setToolTip(self.lang_manager.get_string("custom_emoji_id_tooltip"))

            nitro_lbl = QLabel(self.lang_manager.get_string('nitro_warning'), custom_emoji_window)
            nitro_lbl.setAlignment(Qt.AlignCenter)
            nitro_lbl.resize(175, 22)
            nitro_lbl.move(170, 20)

            set_btn = QPushButton(self.lang_manager.get_string("set"), custom_emoji_window)
            set_btn.resize(155, 25)
            set_btn.move(10, 37)
            set_btn.setFont(QFont(self.btnFontFamily, 10))

            def save_custom_emoji():
                emoji_id = emoji_id_edit.text().strip()
                if emoji_id and not emoji_id.isdigit():
                    logging.error("Failed to set custom emoji: ID is not a digit.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("invalid_emoji_id"))
                    error_window.setIcon(error_window.Warning)
                    error_window.exec_()
                    return

                if emoji_id:
                    self._custom_emoji_id_buffer = emoji_id_edit.text().strip()
                    emoji_edit.setReadOnly(True)
                    emoji_edit.setText('C')
                else:
                    self._custom_emoji_id_buffer = ''
                    emoji_edit.setReadOnly(False)
                    if emoji_edit.text() == 'C':
                        emoji_edit.setText(self._emoji_buffer)

                custom_emoji_window.close()

            emoji_id_edit.setText(self._custom_emoji_id_buffer)

            set_btn.clicked.connect(save_custom_emoji)

            custom_emoji_window.setFocus()
            custom_emoji_window.exec_()
            custom_emoji_window.deleteLater()

        def on_emoji_edit():
            try:
                e_buffer = emoji_edit.text()[:1].encode('utf-8').decode('utf-8')
                self._emoji_buffer = e_buffer
                emoji_edit.setText(e_buffer)
            except (UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError) as error:
                logging.info('An error has occurred while emoji entering: %s', repr(error))
                self._emoji_buffer = ''
                emoji_edit.setText('')

        def save_edited_frame():
            text = text_edit.text().strip()

            if not text:
                if self._emoji_buffer or self._custom_emoji_id_buffer or ''.join(list(self._rpc_buffer.values())):
                    pass
                else:
                    logging.error("Failed to edit frame: Every field is empty.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("input_status"))
                    error_window.setIcon(error_window.Warning)
                    error_window.exec_()
                    text_edit.clear()
                    return

            selected_row = self.frames_list_edit.currentRow()

            edited_frame = {"str": text, "emoji": self._emoji_buffer}
            edited_frame['custom_emoji_id'] = int(self._custom_emoji_id_buffer) if self._custom_emoji_id_buffer else ''
            if ''.join(list(self._rpc_buffer.values())):
                edited_frame['rpc'] = self._rpc_buffer

            self.core.config["frames"][selected_row] = edited_frame

            logging.info('Frame #%s has been edited.', selected_row)

            self.core.config_save()
            self.frames_list_edit_filling()
            self.frames_list_edit.setCurrentRow(selected_row)
            frame_edit_window.close()

        menu_bar = QMenuBar(frame_edit_window)
        menu_bar.setFont(self.font9)
        menu_bar_more = menu_bar.addMenu(self.lang_manager.get_string("more"))
        menu_bar_custom_emoji = QAction(self.lang_manager.get_string("custom_emoji"), frame_edit_window)
        menu_bar_custom_emoji.triggered.connect(set_custom_emoji)
        menu_bar_rpc = QAction('RPC', frame_edit_window)
        menu_bar_rpc.triggered.connect(set_rpc)
        menu_bar_more.addAction(menu_bar_custom_emoji)
        menu_bar_more.addAction(menu_bar_rpc)

        add_btn.clicked.connect(save_edited_frame)
        emoji_edit.textEdited.connect(on_emoji_edit)

        _selected_row_frame = self.core.config["frames"][self.frames_list_edit.currentRow()].copy()
        self._emoji_buffer = _selected_row_frame["emoji"]
        self._custom_emoji_id_buffer = str(_selected_row_frame.get('custom_emoji_id', ''))
        if _selected_row_frame.get('rpc'):
            self._rpc_buffer = _selected_row_frame['rpc']
        else:
            self._rpc_buffer = {}
            self._rpc_buffer['state'] = ''
            self._rpc_buffer['details'] = ''
            self._rpc_buffer['start_timestamp'] = ''
            self._rpc_buffer['end_timestamp'] = ''
            self._rpc_buffer['large_image_key'] = ''
            self._rpc_buffer['large_image_text'] = ''
            self._rpc_buffer['small_image_key'] = ''
            self._rpc_buffer['small_image_text'] = ''

        if self._custom_emoji_id_buffer:
            emoji_edit.setReadOnly(True)
            emoji_edit.setText('C')
        else:
            emoji_edit.setText(self._emoji_buffer)
        text_edit.setText(_selected_row_frame["str"])

        frame_edit_window.setFocus()
        frame_edit_window.exec_()
        frame_edit_window.deleteLater()

    def autostart_on_boot(self):
        if sys.platform not in ('win32',):
            logging.error("Autostart feature cannot be enabled. Not supported platform detected: %s", sys.platform)
            error_window = QMessageBox()
            error_window.setWindowTitle(self.lang_manager.get_string("error"))
            error_window.setWindowIcon(self.icon)
            error_window.setText(self.lang_manager.get_string("autostart_not_supported"))
            error_window.setIcon(error_window.Warning)
            error_window.exec_()
            return

        autostart_on_boot_window = QDialog()
        autostart_on_boot_window.setWindowTitle(self.lang_manager.get_string("autostart_on_boot"))
        autostart_on_boot_window.setWindowIcon(self.icon)
        autostart_on_boot_window.setMinimumSize(QSize(370, 45))
        autostart_on_boot_window.setMaximumSize(QSize(370, 45))
        autostart_on_boot_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        autostart_on_boot_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        enable_btn = QPushButton(self.lang_manager.get_string("enable"), autostart_on_boot_window)
        enable_btn.resize(170, 25)
        enable_btn.move(10, 10)
        enable_btn.setFont(QFont(self.btnFontFamily, 10))

        disable_btn = QPushButton(self.lang_manager.get_string("disable"), autostart_on_boot_window)
        disable_btn.resize(170, 25)
        disable_btn.move(190, 10)
        disable_btn.setFont(QFont(self.btnFontFamily, 10))

        def enable_autostart():
            try:
                if sys.platform == 'win32':
                    if sys.argv[0] == 'main.py': # if the app launches as a script
                        link_args = 'main.py --minimize -r'
                        link_icon_loc = (os.path.join(os.path.abspath(os.getcwd()), 'res/icon.ico'), 0)
                    else: # if compiled by pyinstaller
                        link_args = '--minimize -r' 
                        link_icon_loc = (sys.executable, 0)

                    link_path = os.path.join(winshell.startup(), 'discord-animated-status.lnk')
                    with winshell.shortcut(link_path) as link:
                        link.path = sys.executable
                        link.working_directory = os.path.abspath(os.getcwd())
                        link.arguments = link_args
                        link.icon_location = link_icon_loc
                        link.description = "Discord Animated Status autorun link. You can disable autorun in application."

                logging.info('Autostart on system boot is currently enabled. (%s)', sys.platform)

                success_window = QMessageBox()
                success_window.setWindowTitle(self.lang_manager.get_string("success"))
                success_window.setWindowIcon(self.icon)
                success_window.setIcon(QMessageBox.NoIcon)
                success_window.setText(self.lang_manager.get_string("autostart_enabled"))
                success_window.exec_()
                success_window.deleteLater()

            except Exception as error:
                logging.error("Failed to enable autostart on system boot (%s): %s", sys.platform, repr(error))
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("error_has_occurred") % repr(error))
                error_window.setIcon(QMessageBox.Warning)
                error_window.exec_()
                error_window.deleteLater()

        def disable_autostart():
            try:
                if sys.platform == 'win32':
                    link_path = os.path.join(winshell.startup(), 'discord-animated-status.lnk')

                    if os.path.isfile(link_path):
                        os.remove(link_path)

                logging.info('Autostart on system boot is currently disabled. (%s)', sys.platform)

                success_window = QMessageBox()
                success_window.setWindowTitle(self.lang_manager.get_string("success"))
                success_window.setWindowIcon(self.icon)
                success_window.setIcon(QMessageBox.NoIcon)
                success_window.setText(self.lang_manager.get_string("autostart_disabled"))
                success_window.exec_()
                success_window.deleteLater()

            except Exception as error:
                logging.error("Failed to disable autostart on system boot (%s): %s", sys.platform, repr(error))
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("error_has_occurred") % repr(error))
                error_window.setIcon(QMessageBox.Warning)
                error_window.exec_()
                error_window.deleteLater()

        enable_btn.clicked.connect(enable_autostart)
        disable_btn.clicked.connect(disable_autostart)

        autostart_on_boot_window.setFocus()
        autostart_on_boot_window.exec_()
        autostart_on_boot_window.deleteLater()

    def edit_proxy(self):
        proxy_edit_window = QDialog()
        proxy_edit_window.setWindowTitle(self.lang_manager.get_string("proxy"))
        proxy_edit_window.setWindowIcon(self.icon)
        proxy_edit_window.setMinimumSize(QSize(273, 85))
        proxy_edit_window.setMaximumSize(QSize(273, 85))
        proxy_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        proxy_edit_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        text_edit = QLineEdit(proxy_edit_window)
        text_edit.resize(245, 22)
        text_edit.move(15, 15)

        save_btn = QPushButton(self.lang_manager.get_string("save"), proxy_edit_window)
        save_btn.resize(120, 25)
        save_btn.move(15, 45)
        save_btn.setFont(QFont(self.btnFontFamily, 10))

        info_btn = QPushButton('?', proxy_edit_window)
        info_btn.resize(120, 25)
        info_btn.move(140, 45)
        info_btn.setFont(QFont(self.btnFontFamily, 10))

        def save_proxy():
            proxy = text_edit.text().strip()

            if 'proxies' not in self.core.config:
                self.core.config['proxies'] = {'https': ''}

            self.core.config['proxies']['https'] = proxy
            logging.info('Proxy has been edited.')
            self.core.config_save()

            proxy_edit_window.close()

        def show_info():
            info_window = QDialog()
            info_window.setWindowTitle(self.lang_manager.get_string("proxy"))
            info_window.setWindowIcon(self.icon)
            info_window.setMinimumSize(QSize(185, 145))
            info_window.setMaximumSize(QSize(185, 145))
            info_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            info_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

            lbl = QLabel(self.lang_manager.get_string('proxy_examples'), info_window)
            lbl.move(10, 10)

            text_area = QTextBrowser(info_window)
            text_area.setText(PROXY_EXAMPLES.strip())
            text_area.resize(165, 71)
            text_area.move(10, 30)

            ok_btn = QPushButton('OK', info_window)
            ok_btn.resize(50, 25)
            ok_btn.move(10, 110)
            ok_btn.setFont(QFont(self.btnFontFamily, 10))

            ok_btn.clicked.connect(info_window.close)

            info_window.setFocus()
            info_window.exec_()
            info_window.deleteLater()

        text_edit.setText(self.core.config.get('proxies', {}).get('https', ''))

        save_btn.clicked.connect(save_proxy)
        info_btn.clicked.connect(show_info)

        proxy_edit_window.setFocus()
        proxy_edit_window.exec_()
        proxy_edit_window.deleteLater()

    def default_discord_rpc_edit(self):
        rpc_edit_window, state_edit, details_edit, start_timestamp_edit, end_timestamp_edit, large_image_key_edit, \
        large_image_text_edit, small_image_key_edit, small_image_text_edit = self.get_discord_rpc_window(490, 330)

        lbl = QLabel('CLIENT ID', rpc_edit_window)
        lbl.move(15, 225)
        lbl.setFont(self.whitney_bold_9)

        client_id_edit = QLineEdit(rpc_edit_window)
        client_id_edit.resize(225, 22)
        client_id_edit.move(15, 245)
        client_id_edit.setFont(self.whitney_medium_10)

        rpc_status_lbl = QLabel(rpc_edit_window)
        rpc_status_lbl.resize(225, 40)
        rpc_status_lbl.move(250, 245)
        rpc_status_lbl.setFont(self.whitney_bold_9)
        rpc_status_lbl.setAlignment(Qt.AlignRight)

        continue_btn = QPushButton(self.lang_manager.get_string('save'), rpc_edit_window)
        continue_btn.resize(110, 25)
        continue_btn.move(15, 290)
        continue_btn.setFont(QFont(self.btnFontFamily, 10))

        update_btn = QPushButton(self.lang_manager.get_string('update'), rpc_edit_window)
        update_btn.resize(110, 25)
        update_btn.move(130, 290)
        update_btn.setFont(QFont(self.btnFontFamily, 10))

        disable_btn = QPushButton(rpc_edit_window)
        disable_btn.resize(110, 25)
        disable_btn.move(365, 290)
        disable_btn.setFont(QFont(self.btnFontFamily, 10))

        def on_clock_tick():
            if self.core.rpc.is_connected:
                clock.stop()
                rpc_status_lbl.setText(self.lang_manager.get_string('rpc_status_connected'))
                return

            self._rpc_wait_ticks_buffer += 1
            if self._rpc_wait_ticks_buffer >= 4:
                self._rpc_wait_ticks_buffer = 1

            status_string = self.lang_manager.get_string('rpc_status_connecting') \
                                                         % ('.' * self._rpc_wait_ticks_buffer)
            if self.core.rpc.error:
                if self.core.rpc.error.is_critical:
                    clock.stop()
                    status_string = self.lang_manager.get_string('rpc_status_failed') \
                                    % self.lang_manager.get_string(self.core.rpc.error.lang_string)
                else:
                    status_string += self.lang_manager.get_string('rpc_error_has_occurred') \
                                     % self.lang_manager.get_string(self.core.rpc.error.lang_string)

            rpc_status_lbl.setText(status_string)

        clock = QTimer()
        clock.setTimerType(Qt.PreciseTimer)
        clock.setInterval(200)
        clock.timeout.connect(on_clock_tick)

        self._rpc_wait_ticks_buffer = 0

        def save_rpc_config():
            self.core.config['rpc_client_id'] = client_id_edit.text().strip()
            self.core.config['default_rpc']['state'] = state_edit.text().strip()
            self.core.config['default_rpc']['details'] = details_edit.text().strip()
            self.core.config['default_rpc']['start_timestamp'] = start_timestamp_edit.text().strip()
            self.core.config['default_rpc']['end_timestamp'] = end_timestamp_edit.text().strip()
            self.core.config['default_rpc']['large_image_key'] = large_image_key_edit.text().strip()
            self.core.config['default_rpc']['large_image_text'] = large_image_text_edit.text().strip()
            self.core.config['default_rpc']['small_image_key'] = small_image_key_edit.text().strip()
            self.core.config['default_rpc']['small_image_text'] = small_image_text_edit.text().strip()
            logging.info('Default RPC has been edited.')
            self.core.config_save()

        def save_and_close():
            client_id = client_id_edit.text().strip()
            if client_id:
                if not client_id_edit.text().strip().isdigit():
                    logging.error("Application Client ID is not a digit.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("client_id_is_not_a_digit"))
                    error_window.setIcon(QMessageBox.Warning)
                    error_window.exec_()
                    error_window.deleteLater()
                    return

            save_rpc_config()
            rpc_edit_window.close()

        def update_rpc():
            if self.core.config['disable_rpc']:
                logging.error('RPC cannot be updated. Discord RPC is disabled in config.')
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("rpc_disabled"))
                error_window.setIcon(QMessageBox.Warning)
                error_window.exec_()
                error_window.deleteLater()
                return

            client_id = client_id_edit.text().strip()
            if client_id:
                if not client_id_edit.text().strip().isdigit():
                    logging.error("Application RPC Client ID is not a digit.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("client_id_is_not_a_digit"))
                    error_window.setIcon(QMessageBox.Warning)
                    error_window.exec_()
                    error_window.deleteLater()
                    return
            else:
                logging.error("Application RPC Client ID is empty.")
                error_window = QMessageBox()
                error_window.setWindowTitle(self.lang_manager.get_string("error"))
                error_window.setWindowIcon(self.icon)
                error_window.setText(self.lang_manager.get_string("enter_the_client_id"))
                error_window.setIcon(QMessageBox.Warning)
                error_window.exec_()
                error_window.deleteLater()
                return

            old_client_id = self.core.config['rpc_client_id']
            save_rpc_config()

            if old_client_id != client_id:
                if self.core.rpc:
                    self.core.disconnect_rpc()
                self.core.connect_rpc()

            if self.core.rpc.is_connected:
                try:
                    self.core.rpc.update_rpc(self.core.config['default_rpc'])
                except Exception as error:
                    logging.error("Failed to update Discord RPC: %s", repr(error))
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("error_has_occurred") % repr(error))
                    error_window.setIcon(QMessageBox.Warning)
                    error_window.exec_()
                    error_window.deleteLater()
            else:
                if not clock.isActive():
                    self._rpc_wait_ticks_buffer = 0
                    clock.start()

        def switch_connection():
            new_bool = not self.core.config['disable_rpc']
            logging.info('Boolean of config key "disable_rpc" switched.')

            if new_bool:
                if self.core.rpc:
                    self.core.disconnect_rpc()
                logging.info('Discord RPC disabled.')
                rpc_status_lbl.setText(self.lang_manager.get_string('rpc_status_disabled'))
                clock.stop()
                disable_btn.setText(self.lang_manager.get_string('enable'))

            else:
                client_id = client_id_edit.text().strip()
                if client_id:
                    if not client_id_edit.text().strip().isdigit():
                        logging.error("Application RPC Client ID is not a digit.")
                        error_window = QMessageBox()
                        error_window.setWindowTitle(self.lang_manager.get_string("error"))
                        error_window.setWindowIcon(self.icon)
                        error_window.setText(self.lang_manager.get_string("client_id_is_not_a_digit"))
                        error_window.setIcon(QMessageBox.Warning)
                        error_window.exec_()
                        error_window.deleteLater()
                        return
                else:
                    logging.error("Application RPC Client ID is empty.")
                    error_window = QMessageBox()
                    error_window.setWindowTitle(self.lang_manager.get_string("error"))
                    error_window.setWindowIcon(self.icon)
                    error_window.setText(self.lang_manager.get_string("enter_the_client_id"))
                    error_window.setIcon(QMessageBox.Warning)
                    error_window.exec_()
                    error_window.deleteLater()
                    return

                self.core.config['rpc_client_id'] = client_id

                self.core.connect_rpc()
                logging.info('Discord RPC enabled.')
                disable_btn.setText(self.lang_manager.get_string('disable'))
                self._rpc_wait_ticks_buffer = 0
                clock.start()

            self.core.config['disable_rpc'] = new_bool
            self.core.config_save()

        state_edit.setText(str(self.core.config['default_rpc']['state']))
        details_edit.setText(str(self.core.config['default_rpc']['details']))
        start_timestamp_edit.setText(str(self.core.config['default_rpc']['start_timestamp']))
        end_timestamp_edit.setText(str(self.core.config['default_rpc']['end_timestamp']))
        large_image_key_edit.setText(str(self.core.config['default_rpc']['large_image_key']))
        large_image_text_edit.setText(str(self.core.config['default_rpc']['large_image_text']))
        small_image_key_edit.setText(str(self.core.config['default_rpc']['small_image_key']))
        small_image_text_edit.setText(str(self.core.config['default_rpc']['small_image_text']))
        client_id_edit.setText(str(self.core.config['rpc_client_id']))

        if not self.core.config['disable_rpc'] and self.core.config['rpc_client_id']:
            disable_btn.setText(self.lang_manager.get_string('disable'))
            if self.core.rpc:
                if self.core.rpc.is_connected:
                    rpc_status_lbl.setText(self.lang_manager.get_string('rpc_status_connected'))
                else:
                    clock.start()
        else:
            disable_btn.setText(self.lang_manager.get_string('enable'))
            rpc_status_lbl.setText(self.lang_manager.get_string('rpc_status_disabled'))

        continue_btn.clicked.connect(save_and_close)
        update_btn.clicked.connect(update_rpc)
        disable_btn.clicked.connect(switch_connection)

        rpc_edit_window.setFocus()
        rpc_edit_window.exec_()
        clock.stop()
        rpc_edit_window.deleteLater()

    def about(self):
        about_window = QDialog()
        about_window.setWindowTitle(self.lang_manager.get_string("about"))
        about_window.setWindowIcon(self.icon)
        about_window.setMinimumSize(QSize(350, 250))
        about_window.setMaximumSize(QSize(350, 250))
        about_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        about_window_bg_label = QLabel("", about_window)
        about_window_bg_label.setAlignment(Qt.AlignCenter)
        about_window_bg_label.resize(350, 250)

        y = 0
        for k in AUTHORS_M:
            lbl = QLabel(k, about_window)
            lbl.setFont(self.font7)
            lbl.setAlignment(Qt.AlignCenter)
            txt_width = lbl.fontMetrics().boundingRect(lbl.text()).width()
            txt_height = lbl.fontMetrics().boundingRect(lbl.text()).height()
            lbl.move(350/2-txt_width/2, 250/2+(txt_height*y)-30)
            y += 1

        about_window_version_label = QLabel("Version: %s" % VERSION_M, about_window)
        about_window_version_label.setFont(self.font10)
        about_window_version_label.setAlignment(Qt.AlignCenter)
        txt_width = about_window_version_label.fontMetrics().boundingRect(about_window_version_label.text()).width()
        about_window_version_label.move(350/2-txt_width/2, 250/2+40)

        about_window_bg = QMovie("res/images/about-bg.gif")
        about_window_bg_label.setMovie(about_window_bg)
        about_window_bg.start()

        about_window.exec_()
        about_window.deleteLater()

    def get_discord_rpc_window(self, width, height):
        rpc_edit_window = QDialog()
        rpc_edit_window.setWindowTitle("Discord RPC")
        rpc_edit_window.setWindowIcon(self.icon)
        rpc_edit_window.setMinimumSize(QSize(width, height))
        rpc_edit_window.setMaximumSize(QSize(width, height))
        rpc_edit_window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        rpc_edit_window.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")

        lbl = QLabel('STATE', rpc_edit_window)
        lbl.move(15, 15)
        lbl.setFont(self.whitney_bold_9)

        state_edit = QLineEdit(rpc_edit_window)
        state_edit.resize(225, 22)
        state_edit.move(15, 35)
        state_edit.setFont(self.whitney_medium_10)

        lbl = QLabel('DETAILS', rpc_edit_window)
        lbl.move(250, 15)
        lbl.setFont(self.whitney_bold_9)

        details_edit = QLineEdit(rpc_edit_window)
        details_edit.resize(225, 22)
        details_edit.move(250, 35)
        details_edit.setFont(self.whitney_medium_10)

        lbl = QLabel('START TIMESTAMP', rpc_edit_window)
        lbl.move(15, 65)
        lbl.setFont(self.whitney_bold_9)

        start_timestamp_edit = QLineEdit(rpc_edit_window)
        start_timestamp_edit.resize(225, 22)
        start_timestamp_edit.move(15, 85)
        start_timestamp_edit.setFont(self.whitney_medium_10)
        start_timestamp_edit.setToolTip(self.lang_manager.get_string('rpc_timestamp_tooltip'))

        lbl = QLabel('END TIMESTAMP', rpc_edit_window)
        lbl.move(250, 65)
        lbl.setFont(self.whitney_bold_9)

        end_timestamp_edit = QLineEdit(rpc_edit_window)
        end_timestamp_edit.resize(225, 22)
        end_timestamp_edit.move(250, 85)
        end_timestamp_edit.setFont(self.whitney_medium_10)
        end_timestamp_edit.setToolTip(self.lang_manager.get_string('rpc_timestamp_tooltip'))

        lbl = QLabel('LARGE IMAGE KEY', rpc_edit_window)
        lbl.move(15, 115)
        lbl.setFont(self.whitney_bold_9)

        large_image_key_edit = QLineEdit(rpc_edit_window)
        large_image_key_edit.resize(225, 22)
        large_image_key_edit.move(15, 135)
        large_image_key_edit.setFont(self.whitney_medium_10)

        lbl = QLabel('LARGE IMAGE TEXT', rpc_edit_window)
        lbl.move(250, 115)
        lbl.setFont(self.whitney_bold_9)

        large_image_text_edit = QLineEdit(rpc_edit_window)
        large_image_text_edit.resize(225, 22)
        large_image_text_edit.move(250, 135)
        large_image_text_edit.setFont(self.whitney_medium_10)

        lbl = QLabel('SMALL IMAGE KEY', rpc_edit_window)
        lbl.move(15, 165)
        lbl.setFont(self.whitney_bold_9)

        small_image_key_edit = QLineEdit(rpc_edit_window)
        small_image_key_edit.resize(225, 22)
        small_image_key_edit.move(15, 185)
        small_image_key_edit.setFont(self.whitney_medium_10)

        lbl = QLabel('SMALL IMAGE TEXT', rpc_edit_window)
        lbl.move(250, 165)
        lbl.setFont(self.whitney_bold_9)

        small_image_text_edit = QLineEdit(rpc_edit_window)
        small_image_text_edit.resize(225, 22)
        small_image_text_edit.move(250, 185)
        small_image_text_edit.setFont(self.whitney_medium_10)

        return rpc_edit_window, state_edit, details_edit, start_timestamp_edit, end_timestamp_edit, \
               large_image_key_edit, large_image_text_edit, small_image_key_edit, small_image_text_edit

    def reload_config(self):
        logging.info('Config reloading...')
        self.core.config_load()
        self.core.apply_config()

    def speed_change(self):
        if self.speed_edit.value() != self.core.config["delay"]:
            self.core.config["delay"] = self.speed_edit.value()
            logging.info('Frame updating delay has been changed.')
            self.core.config_save()

    def switch_frames_randomizing(self):
        self.core.config["randomize_frames"] = not self.core.config["randomize_frames"]
        logging.info('Boolean of config key "randomize_frames" switched.')
        self.core.config_save()

    def update_frame_screen(self):
        self.current_frame_screen.setText(self.current_frame)

    def update_info_screen(self):
        self.info_screen.setText(self.current_info)

    def on_requests_thread_stop(self):
        self.run_btn.setEnabled(True)

        self.run_stop_animated_status.setText(self.lang_manager.get_string("launch"))
        self.run_stop_animated_status.setEnabled(True)
        self.run_stop_animated_status.disconnect()
        self.run_stop_animated_status.triggered.connect(self.run_animation)

        self.current_frame_screen.setText("")
        self.info_screen.setText("")

    def on_auth_failed(self):
        self.stop_animation()

        if not self.isHidden():
            error_window = QMessageBox()
            error_window.setWindowTitle(self.lang_manager.get_string("error"))
            error_window.setWindowIcon(self.icon)
            error_window.setText(self.lang_manager.get_string("auth_failed"))
            error_window.setIcon(error_window.Warning)
            error_window.exec_()
            error_window.deleteLater()
        else:
            self.tray_icon.showMessage("Discord Animated Status",
                                       self.lang_manager.get_string("auth_failed"),
                                       self.icon, msecs=1000)

    def changeEvent(self, event):
        if self.windowState() == Qt.WindowMinimized:
            self.hide()
            logging.info('Program window has been minimized.')

    def tray_click_checking(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.maximize_window()
            logging.info('Program window has been maximized by tray icon click.')

    def maximize_window(self):
        self.show()
        self.showNormal()

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def closeEvent(self, event):
        self.tray_icon.hide()
        if self.core.config['rpc_client_id'] and not self.core.config['disable_rpc']:
            if self.core.rpc:
                self.core.disconnect_rpc()

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

def init_gui_application(launch_args):
    for folder in RESOURCES_DIR:
        if folder == 'files':
            folder_name = ''
        else:
            folder_name = folder

        for filename in RESOURCES_DIR[folder]:
            filepath = os.path.join('res', folder_name, filename)

            if not os.path.isfile(filepath):
                logging.critical('Application resources not found: %s', filepath)
                return 2

    logging.info('GUI initialization...')
    app = QApplication(sys.argv)
    apply_style(app)
    App(launch_args)
    code = app.exec_()

    return code
