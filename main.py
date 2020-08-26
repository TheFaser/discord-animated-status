from PyQt5 import QtWidgets

from gui import App, apply_style
from required import sys, logging

def entry():
    """Application entry point."""
    logging.basicConfig(filename="last.log", level=logging.INFO, format="%(asctime)-15s | %(levelname)s | %(message)s")

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
