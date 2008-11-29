"""
Program main entry point.

Responsible for processing command line options and initializing the
application.
"""


from sys import argv
from optparse import OptionParser
import logging

import wx

from gui import MainFrame


def parse_options():
    op = OptionParser(usage="%prog [options] [filename]", version="%prog 0.1")
    op.add_option("-l", "--log-level", type="int", default=logging.ERROR,
                  help="specify log level (0 to log everything)")
    op.add_option("-f", "--log-file", default=None,
                  help="specify a file to send log messages to")
    # We skip first command line argument since it is the name of the program
    return op.parse_args(argv[1:])


def setup_logging(level, file):
    format= "%(asctime)s [%(levelname)s] %(message)s" 
    # Setup logging to stderror
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(format))
    consoleHandler.setLevel(level)
    logging.getLogger().addHandler(consoleHandler)
    # Setup logging to file
    if file:
        fileHandler = logging.FileHandler(file, "w")
        fileHandler.setFormatter(logging.Formatter(format))
        fileHandler.setLevel(level)
        logging.getLogger().addHandler(fileHandler)
    logging.getLogger().setLevel(level)
    logging.info("Logging set up with level=%s, file=%s", level, file)


def main():
    (options, input_files) = parse_options()
    setup_logging(options.log_level, options.log_file)
    app = wx.PySimpleApp()
    main_frame = MainFrame()
    main_frame.Show()
    # Must be called after Show() because window size is not set before that
    main_frame.open_timeline(input_files)
    app.MainLoop()


if __name__ == '__main__':
    main()
