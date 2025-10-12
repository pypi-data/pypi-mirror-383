#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import faulthandler
import logging
import logging.handlers
import sys

from .meta_data import PROGRAMNAME
from .app_dirs import data_directories
import mtg_proxy_printer.settings

root_logger = logging.getLogger(PROGRAMNAME)
LOG_FORMAT = "%(asctime)s %(levelname)s - %(name)s - %(message)s"
LOG_DIR = data_directories.user_log_path
LOG_DIR.mkdir(parents=True, exist_ok=True)
try:
    _CRASH_LOG_FILE = open(LOG_DIR / f"{PROGRAMNAME}-crashes.log", "at", encoding="utf-8")
    faulthandler.enable(_CRASH_LOG_FILE, all_threads=True)
except PermissionError:
    pass

__all__ = [
    "get_logger",
    "configure_root_logger",
]


def get_logger(full_module_path: str) -> logging.Logger:
    """
    Returns a logger instance for the given module __name__.
    """
    module_path = ".".join(full_module_path.split(".")[1:])
    return root_logger.getChild(module_path)


def configure_root_logger(output_stdout: bool = True):
    """
    Initialize the logging system.
    """
    global _CRASH_LOG_FILE
    debug_settings = mtg_proxy_printer.settings.settings["debug"]
    file_log_level = debug_settings["log-level"]
    root_logger.setLevel(1)
    if output_stdout:
        std_out_handler = logging.StreamHandler(sys.stdout)
        std_out_handler.setLevel(file_log_level)
        std_out_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(std_out_handler)
    if debug_settings.getboolean("cutelog-integration"):
        socket_handler = logging.handlers.SocketHandler("127.0.0.1", 19996)  # default listening address
        root_logger.addHandler(socket_handler)
        root_logger.info(f"""Connected logger "{root_logger.name}" to local log server.""")
    if debug_settings.getboolean("write-log-file"):
        log_file_path = LOG_DIR / f"{PROGRAMNAME}.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file_path, "D", 1, 10, "utf-8", True)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(file_handler)
