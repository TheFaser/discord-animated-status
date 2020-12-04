import os
import sys
import logging
import argparse
from datetime import datetime

from gui import init_gui_application

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

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-m', '--minimize', action='store_true', help='minimize app to tray on launch')
    args_parser.add_argument('-r', '--run-animation', action='store_true', help='run status animation on launch')
    try:
        launch_args = args_parser.parse_args()
        logging.info('Launch arguments: %s', launch_args.__dict__)
    except SystemExit as error:
        logging.critical('SystemExit caught. Failed to parse launch arguments.')
        exit_code = 160

    try:
        exit_code = init_gui_application(launch_args)
    except Exception as error:
        logging.critical('Failed to init GUI: %s', repr(error))

    logging.info("Program exit with code %s.", exit_code)
    if exit_code != 0:
        logging.warning("Program exit code was not 0. This means something went wrong while executing the program.")

    logging.info("--- LOG END ---")
    sys.exit(exit_code)

if __name__ == '__main__':
    entry()
