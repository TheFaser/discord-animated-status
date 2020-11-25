from required import json, logging

class LanguageManager(object):
    """A class responsible for localization."""

    def __init__(self):
        self.selected_lang = "en"
        self.supported_langs = []
        self.text_data = {}

        self.init_text_data()

    def get_string(self, string):
        """Returns a localized string."""
        try:
            return self.text_data[self.selected_lang][string]
        except KeyError:
            logging.error("Could not find textdata string '%s' for '%s' language!", string, self.selected_lang)

    def load_language(self, lang):
        """Load language data from a config file."""
        if lang in self.supported_langs:
            self.selected_lang = lang
            logging.info('Selected lang is %s', str(lang).upper())
        else:
            logging.warning("Selected lang not supported! Setting current language to EN.")
            self.selected_lang = "en"

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
        with open("res/lang.json", "r+", encoding="utf-8") as lang_file:
            self.text_data = json.load(lang_file)
            for k in self.text_data.keys():
                self.supported_langs.append(k)
