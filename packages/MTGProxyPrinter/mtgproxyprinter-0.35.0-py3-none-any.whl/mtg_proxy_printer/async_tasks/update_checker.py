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


import random
import re
import socket
import sqlite3
import ssl
import urllib.parse
import urllib.error

import ijson
from PySide6.QtCore import QObject, Signal

from mtg_proxy_printer.argument_parser import Namespace
import mtg_proxy_printer.meta_data
from mtg_proxy_printer import settings
from mtg_proxy_printer.async_tasks.downloader_base import DownloaderBase
from mtg_proxy_printer.model.carddb import CardDatabase, SCHEMA_NAME
from mtg_proxy_printer.async_tasks.card_info_downloader import ApiStreamTask
from mtg_proxy_printer.natsort import natural_sorted, str_less_than
from mtg_proxy_printer.sqlite_helpers import cached_dedent, open_database
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.units_and_sizes import OptStr

logger = get_logger(__name__)
del get_logger

__all__ = [
    "UpdateChecker",
]

VERSION_TAG_MATCHER = re.compile(r"v(?P<version>\d+\.\d+\.\d+)")
KNOWN_APPLICATION_MIRRORS: list[str] = [
    "http://chiselapp.com/user/luziferius/repository/MTGProxyPrinter",
    # Don’t use the master repository for now, as it may not be able to handle load spikes
    # "http://1337net.duckdns.org:8080/MTGProxyPrinter",
]


class CardDataUpdateCheckTask(ApiStreamTask):
    card_data_update_found = Signal(int)

    def __init__(self, card_db: CardDatabase, db: sqlite3.Connection = None):
        super().__init__()
        self.card_db = card_db
        self._db = db

    @property
    def db(self) -> sqlite3.Connection:
        # Delay connection creation until first access.
        # Avoids opening connections that aren't actually used and opens the connection
        # in the thread that actually uses it.
        if self._db is None:
            logger.debug(f"{self.__class__.__name__}.db: Opening new database connection")
            self._db = open_database(self.card_db.db_path, SCHEMA_NAME)
        return self._db

    def perform_card_data_update_check(self):
        if not self.card_database_has_data():
            logger.info("Card database has no data. Not checking for updates.")
            return
        logger.info("Checking for card data updates.")
        total_cards_available, total_cards_in_last_update = self._is_newer_card_data_available()
        if total_cards_available and total_cards_available > total_cards_in_last_update:
            new_cards = total_cards_available - total_cards_in_last_update
            logger.info(f"New card data is available: {new_cards} new cards. Notifying the user.")
            self.card_data_update_found.emit(new_cards)
        else:
            logger.debug("No new card data found.")

    def _is_newer_card_data_available(self) -> tuple[int, int]:
        total_cards_in_last_update = self.get_total_cards_in_last_update()
        total_cards_available = self.get_available_card_count()
        logger.debug(f"Total cards during last update: {total_cards_in_last_update}")
        return total_cards_available, total_cards_in_last_update

    def get_total_cards_in_last_update(self) -> int:
        """
        Returns the latest card timestamp from the LastDatabaseUpdate table.
        Returns today(), if the table is empty.
        """
        query = cached_dedent("""\
        SELECT MAX(update_id), reported_card_count -- get_total_cards_in_last_update()
            FROM LastDatabaseUpdate
        """)
        id_, total_cards_in_last_update = self.db.execute(query).fetchone()
        return 0 if id_ is None else total_cards_in_last_update

    def card_database_has_data(self) -> bool:
        result, = self.db.execute("SELECT EXISTS(SELECT * FROM Card)\n").fetchone()
        return bool(result)

    def run(self):
        try:
            self.perform_card_data_update_check()
        except ValueError:
            logger.info("Card data update check cancelled.")
        except ssl.SSLError as e:
            logger.exception(f"Update check failed: {e}")


class ApplicationUpdateCheckTask(DownloaderBase):
    application_update_found = Signal(str)

    def run(self):
        try:
            self.perform_application_update_check()
        except ValueError:
            logger.info("Application update check cancelled.")
        except ssl.SSLError as e:
            logger.exception(f"Update check failed: {e}")

    def perform_application_update_check(self):
        logger.info("Checking for application updates.")
        if result := self._is_newer_application_version_available():
            logger.info(f"A new update is available: {result}. Notifying the user.")
            self.application_update_found.emit(result)
        else:
            logger.debug("No application update found.")

    def _is_newer_application_version_available(self) -> OptStr:
        available_versions = self._read_available_application_versions()
        if available_versions and str_less_than(mtg_proxy_printer.meta_data.__version__, available_versions[0]):
            return available_versions[0]
        return None

    @staticmethod
    def _get_application_mirrors() -> list[str]:
        mirrors = KNOWN_APPLICATION_MIRRORS.copy()
        random.shuffle(mirrors)
        return mirrors

    def _read_available_application_versions(self) -> list[str]:
        """
        Reads the available versions from any known mirror
        :returns: list of all released versions, sorted descending.
        """
        tags = []
        for mirror in self._get_application_mirrors():
            try:
                if tags := self._read_available_application_versions_from_mirror(mirror):
                    break
            except (urllib.error.URLError, socket.timeout, ijson.IncompleteJSONError) as e:
                logger.warning(f"Failed to read update from mirror {mirror}. Reason: {e}")
                continue
        return tags

    def _read_available_application_versions_from_mirror(self, mirror):
        data, _ = self.read_from_url(
            f"{mirror}/json/tag/list/",
            self.tr("Application update check: ", "Progress bar label text"))
        items = ijson.items(data, "payload.tags.item", use_float=True)
        matches = filter(
            None,
            map(VERSION_TAG_MATCHER.fullmatch, items)
        )
        return natural_sorted((match["version"] for match in matches), reverse=True)


class UpdateChecker(QObject):
    """The interface class."""
    card_data_update_found = Signal(int)
    application_update_found = Signal(str)
    network_error_occurred = Signal(str)
    request_run_async_task = Signal(AsyncTask)

    def __init__(self, card_db: CardDatabase, args: Namespace, parent: QObject = None):
        logger.info(f"Creating {self.__class__.__name__} instance.")
        super().__init__(parent)
        self.card_db = card_db
        # Don’t do the card data update check, if the user imports card data via command line arguments
        self.card_data_parameter_passed = bool(args.card_data and args.card_data.is_file())
        logger.info(f"Created {self.__class__.__name__} instance.")

    def check_for_updates(self):
        section = settings.settings["update-checks"]
        if section.getboolean("check-for-application-updates"):
            logger.debug("Enqueue application update check")
            task = ApplicationUpdateCheckTask()
            task.network_error_occurred.connect(self.network_error_occurred)
            task.application_update_found.connect(self.application_update_found)
            self.request_run_async_task.emit(task)
        else:
            logger.info("Not running application update check")
        if not self.card_data_parameter_passed and section.getboolean("check-for-card-data-updates"):
            logger.debug("Enqueue card data update check")
            task = CardDataUpdateCheckTask(self.card_db)
            task.network_error_occurred.connect(self.network_error_occurred)
            task.card_data_update_found.connect(self.card_data_update_found)
            self.request_run_async_task.emit(task)
        else:
            logger.info("Not running card data update check")
