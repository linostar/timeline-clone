"""
Program main entry point.

Responsible for processing command line options and initializing the
application.
"""


from sys import argv
from optparse import OptionParser
import logging
from logging import info as loginfo

import wx

from gui import MainFrame
from version import get_version
import config


def parse_options():
    """Parse command line options using the optparse module."""
    version_string = "%prog " + get_version()
    option_parser = OptionParser(usage="%prog [options] [filename]",
                                 version=version_string)
    option_parser.add_option("-l", "--log-level",
                             type="int", default=logging.ERROR,
                             help="specify log level (0 to log everything)")
    option_parser.add_option("-f", "--log-file",
                             default=None,
                             help="specify a file to send log messages to")
    # Skip first command line argument since it is the name of the program
    return option_parser.parse_args(argv[1:])


def setup_logging(log_level, filename):
    """
    Setup default logger to log to stderror and possible also to a file.

    The default logger is used like this:

        import logging
        logging.error(...)
    """
    format= "%(asctime)s [%(levelname)s] %(message)s"
    # Setup logging to stderror
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    console_handler.setLevel(log_level)
    logging.getLogger().addHandler(console_handler)
    # Setup logging to file if filename is specified
    if filename:
        file_handler = logging.FileHandler(filename, "w")
        file_handler.setFormatter(logging.Formatter(format))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(log_level)
    loginfo("Logging set up with log level=%s, filename=%s", log_level,
            filename)


def create_wx_app(input_files):
    """Initialize wx and create the main frame."""
    app = wx.PySimpleApp()
    main_frame = MainFrame()
    main_frame.Show()
    for input_file in input_files:
        main_frame.display_timeline(input_file)
    return app


def main():
    """Main entry point."""
    (options, input_files) = parse_options()
    setup_logging(options.log_level, options.log_file)
    config.read()
    app = create_wx_app(input_files)
    app.MainLoop()


if __name__ == '__main__':
    main()
