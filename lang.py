from required import json, logging

class LanguageManager:
    """A class responsible for localization."""

    def __init__(self):
        self.selected_lang = "en"
        self.supported_langs = ["en", "ru"]
        self.text_data = {}

        self.init_text_data()

    def get_string(self, string):
        """Returns a localized string."""
        try:
            return self.text_data[string][self.selected_lang]
        except KeyError:
            logging.error("Could not find textdata string '%s' for '%s' language!", string, self.selected_lang)

    def load_language(self):
        """Load language data from a config file."""
        config = {}
        try:
            with open("config.json", encoding="utf-8") as cfg_file:
                config = json.load(cfg_file)
        except:
            logging.warning("Failed to load language data! Setting current language to EN.")
            self.selected_lang = "en"
            return
        try:
            if config["language"] in self.supported_langs:
                self.selected_lang = config["language"]
                return
            logging.warning("Failed to load language data! Setting current language to EN.")
            self.selected_lang = "en"
            return
        except:
            logging.warning("Failed to load language data! Setting current language to EN.")
            self.selected_lang = "en"
            return

    def save_language(self):
        """Save language data to a config file."""
        try:
            with open("config.json", "r+", encoding="utf-8") as cfg_file:
                cfg = json.load(cfg_file)

                cfg["language"] = self.selected_lang

                cfg_file.seek(0)
                json.dump(cfg, cfg_file, ensure_ascii=False, indent=4)
                cfg_file.truncate()
        except:
            logging.error("Failed to save language data!")
            return

    def init_text_data(self):
        """Initialize text data for language manager. Called once upon init."""
        self.text_data["launch"] = {"ru": "Запустить", "en": "Launch"}
        self.text_data["launch_info"] = {"ru": "Запуск анимированного статуса", "en": "Launch animated status"}
        self.text_data["quit"] = {"ru": "Выйти", "en": "Quit"}
        self.text_data["animated_frame_list"] = {"ru": "Список кадров для анимированного статуса", "en": "Animated status frame list"}
        self.text_data["save"] = {"ru": "Сохранить", "en": "Save"}
        self.text_data["load"] = {"ru": "Загрузить", "en": "Load"}
        self.text_data["about"] = {"ru": "Справка", "en": "About"}
        self.text_data["language"] = {"ru": "Язык", "en": "Language"}
        self.text_data["config"] = {"ru": "Настройки", "en": "Settings"}
        self.text_data["move_up_tooltip"] = {"ru":"Переместить вверх", "en":"Move up"}
        self.text_data["move_down_tooltip"] = {"ru":"Переместить вниз", "en":"Move down"}
        self.text_data["add_frame"] = {"ru": "Добавить кадр", "en": "Add frame"}
        self.text_data["new_frame"] = {"ru": "Новый кадр", "en": "New frame"}
        self.text_data["add_frame_tooltip"] = {"ru": "Добавить кадр:", "en": "Add frame:"}
        self.text_data["remove_selected_frame"] = {"ru": "Удалить выбранный в списке кадр", "en": "Remove selected frame"}
        self.text_data["current_frame"] = {"ru": "Сейчас отображается кадр:", "en": "Current frame:"}
        self.text_data["current_displayed_frame"] = {"ru": "Статус который в данный момент\nотображается в Discord", "en": "Currently displayed frame in\nyour Discord status"}
        self.text_data["info"] = {"ru": "Информация о работе:", "en": "Information log:"}
        self.text_data["more_info"] = {"ru": "Отображение дополнительной информации:\nОшибки в работе и т.д.", "en": "Displaying extra info:\nExceptions in runtime and etc."}
        self.text_data["delay_s"] = {"ru": "Задержка в секундах:", "en": "Delay in seconds:"}
        self.text_data["save_error"] = {"ru": "Не удалось сохранить настрйоки.", "en": "Failed to save settings."}
        self.text_data["delay_info"] = {"ru": "Задержка между сменой кадров", "en": "Delay between frame switch"}
        self.text_data["stop"] = {"ru": "Остановить", "en": "Stop"}
        self.text_data["stop_info"] = {"ru": "Остановить анимацию статуса\nМожет потребоваться время", "en": "Stop animated status\nMay take some time"}
        self.text_data["your_token"] = {"ru": "Ваш токен Discord", "en": "Your Discord token"}
        self.text_data["your_token_tooltip"] = {"ru": "Ваш токен Discord:\n", "en": "Your Discord token:\n"}
        self.text_data["xrate_exceeded"] = {"ru": "Discord XRate превышен. Подождите 30с.", "en": "Discord XRate exceeded. Sleeping for 30s."}
        self.text_data["error"] = {"ru": "Ошибка", "en": "Error"}
        self.text_data["frame_list_empty"] = {"ru": "Список кадров пуст.", "en": "Frame list is empty."}
        self.text_data["input_token"] = {"ru": "Введите свой токен Discord.", "en": "Enter your Discord token."}
        self.text_data["request_error"] = {"ru": "Не удалось отправить запрос на сервера Discord: \n", "en": "Failed to send request to Discord servers: \n"}
        self.text_data["stopping"] = {"ru": "Остановка...", "en": "Stopping..."}
        self.text_data["input_status"] = {"ru": "Введите статус", "en": "Enter status"}
        self.text_data["add"] = {"ru": "Добавить", "en": "Add"}
        self.text_data["clear"] = {"ru": "Очистить", "en": "Clear"}
        self.text_data["regex"] = {"ru":"", "en":""}
        self.text_data["clear_tooltip"] = {"ru": "Очистить список кадров", "en": "Clear frame list"}
        self.text_data["edit_frame"] = {"ru": "Редактирование кадра", "en": "Edit frame"}
        self.text_data["edit_frame_tooltip"] = {"ru": "Редактировать кадр:", "en": "Edit frame:"}
        self.text_data["parse_error"] = {"ru": "Не удалось обработать кадр", "en": "Failed to parse frame"}
        self.text_data["unhide_token"] = {"ru": "Разверните полностью окно чтобы ввести токен.", "en": "Resize the GUI window to it's full size to enter the token."}
    