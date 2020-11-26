import os
import sys
import logging
from datetime import datetime

from PyQt5 import QtWidgets

from gui import App, apply_style

def entry():
    """Application entry point."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_formatter_string = '%(asctime)s | %(levelname)s |%(filename)s:%(lineno)d| %(message)s'
    log_formatter = logging.Formatter(log_formatter_string, datefmt='%Y-%m-%d-%H:%M:%S')
    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'

    file_handler = logging.FileHandler(os.path.join('logs', log_filename))
    file_handler.setFormatter(log_formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    logging.basicConfig(handlers=[file_handler, console_handler], level=logging.DEBUG)

    logging.info("--- LOG START ---")

    win = QtWidgets.QApplication(sys.argv)
    apply_style(win)
    App()
    code = win.exec_()

    logging.info("Program exit with code %d.", code)
    if code != 0:
        logging.warning("Program exit code was not 0. This means something went wrong while executing the program.")
    
    logging.info("--- LOG END ---")
    sys.exit(code)

if __name__ == '__main__':
    entry()
