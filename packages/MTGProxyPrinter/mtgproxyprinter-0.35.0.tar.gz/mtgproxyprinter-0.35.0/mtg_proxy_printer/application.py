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


import atexit
from functools import partial
import os
import pathlib
import platform
import shutil
import sys
from tempfile import mkdtemp

from PySide6.QtCore import Slot, QTimer, QStringListModel, QThreadPool, QTranslator, QLocale, QLibraryInfo, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from mtg_proxy_printer.argument_parser import Namespace
from mtg_proxy_printer import meta_data, BlockingQueuedConnection
import mtg_proxy_printer.model.carddb
import mtg_proxy_printer.carddb_migrations
import mtg_proxy_printer.model.document
import mtg_proxy_printer.model.imagedb
from mtg_proxy_printer.async_tasks.card_info_downloader import FileStreamTask, DatabaseImportTask
from mtg_proxy_printer.carddb_migrations import DatabaseMigrationTask
from mtg_proxy_printer.async_tasks.document_loader import DocumentLoader
from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
from mtg_proxy_printer import settings
from mtg_proxy_printer.async_tasks.update_checker import UpdateChecker
import mtg_proxy_printer.async_tasks.card_info_downloader
import mtg_proxy_printer.ui.common
import mtg_proxy_printer.ui.main_window
import mtg_proxy_printer.ui.settings_window
import mtg_proxy_printer.progress_meter
from mtg_proxy_printer.async_tasks.base import AsyncTask, AsyncTaskRunner
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger

__all__ = [
    "Application",
]


class Application(QApplication):

    def __init__(self, args: Namespace, argv: list[str] = None):
        if argv is None:
            argv = sys.argv
        logger.info(f"Starting MTGProxyPrinter version {meta_data.__version__}")
        super().__init__(argv)
        # Note: The sub-expression '"-style" not in argv' breaks, if "-style" is passed as a value for another
        # argument or as a positional argument.
        # (For example, if the user wants to load a document with file name "-style" via command line argument.)
        if platform.system() == "Windows" and "-style" not in argv and not os.getenv("QT_STYLE_OVERRIDE"):
            logger.info("Running on Windows without explicit style set. Use 'fusion', which supports dark mode.")
            # Set a dark-mode compatible style, if on Windows and the user does not override the style.
            self.setStyle("fusion")
        # Used by the with_database_write_lock decorator to not start un-frozen,
        # waiting tasks when the application is about to exit
        self.should_run = True
        self.args = args
        self._setup_translations()
        self._setup_icons()
        self.language_model = self._create_language_model()  # TODO: Can this be removed?
        self.card_db, self.image_db = self._open_databases(args)
        self.document = self._create_document_instance(self.card_db, self.image_db)
        logger.debug("Creating GUI")
        self.main_window = mtg_proxy_printer.ui.main_window.MainWindow(
            self.card_db, self.image_db, self.document, self.language_model
        )
        self.main_window.request_run_async_task.connect(self.run_async_task)
        self.update_checker = self._create_update_checker(args)
        self.main_window.ui.action_download_card_data.setEnabled(False)
        self.settings_window = self._create_settings_window(
            self.language_model, self.document, self.main_window)
        if settings.settings["gui"].getboolean("gui-open-maximized"):
            self.main_window.showMaximized()
        else:
            self.main_window.show()

    def enqueue_startup_tasks(self, _: Namespace):
        """
        Enqueues all tasks that should run in the Qt event loop at application start.
        Includes
        - Settings migration and change-log display after application updates
        - checking for updates or undecided update policy settings
        - notifying on empty card database
        - running the card data import, if a JSON card data document is given as a command line argument
        - opening a document given via command line arguments
        - etc…
        """
        if settings.was_application_updated():
            logger.info(
                f'Updated application from {settings.settings["update-checks"]["last-used-version"]} '
                f'to {meta_data.__version__}')
            settings.update_stored_version_string()
            settings.write_settings_to_file()
            QTimer.singleShot(0, self.main_window.about_dialog.show_changelog)
        logger.debug("Enqueueing update check")
        QTimer.singleShot(100, self._check_for_undecided_update_settings)
        task = DatabaseMigrationTask(self.card_db)
        task.task_completed.connect(self._on_carddb_migrations_completed)
        self.run_async_task(task)

    @Slot()
    def _on_carddb_migrations_completed(self):
        self.card_db.reopen_database()
        logger.debug(
            "Card database migrations completed. Database re-opened. Checking if the printing filters need updates.")
        printing_filter_updater_runner = PrintingFilterUpdater(self.card_db)
        printing_filter_updater_runner.task_completed.connect(self._on_printing_filter_updater_completed)
        self.run_async_task(printing_filter_updater_runner)

    @Slot()
    def _on_printing_filter_updater_completed(self):
        logger.debug("Printing filters synchronized with settings.")
        self.main_window.ui.action_download_card_data.setEnabled(self.card_db.allow_updating_card_data())
        self.main_window.update_language_model()
        self.update_checker.check_for_updates()
        self._handle_command_line_argument_files()

    def _handle_command_line_argument_files(self):
        args = self.args
        if args.card_data and args.card_data.is_file():
            logger.info(f"User imports card data from file {args.card_data}")
            self.run_async_task(data_source := FileStreamTask(args.card_data))
            self.run_async_task(DatabaseImportTask(data_source, carddb_path=self.card_db.db_path))
        elif not self.card_db.has_data():
            logger.info("Card database is empty. Will ask the user, if they choose to download the data now.")
            self.main_window.ask_user_about_empty_database()
        if args.file is not None:
            if args.file.is_file():
                QTimer.singleShot(0, lambda: self.run_async_task(DocumentLoader(self.document, args.file)))
                logger.info(f'Enqueued loading of document "{args.file}"')
            elif args.file.exists():
                logger.warning(f'Command line argument "{args.file}" exists, but is not a file. Not loading it.')
            else:
                logger.warning(f'Command line argument "{args.file}" does not exist. Ignoring it.')

    def _open_databases(self, args: Namespace):
        if args.test_exit_on_launch:
            temp_directory = pathlib.Path(mkdtemp())
            logger.info(f"Opening databases in temporary directory {temp_directory}")
            atexit.register(partial(shutil.rmtree, temp_directory))
            card_db = mtg_proxy_printer.model.carddb.CardDatabase(temp_directory / "card_db" / "CardDatabase.sqlite3")
            image_db = mtg_proxy_printer.model.imagedb.ImageDatabase(
                temp_directory/"image_db", parent=self)
            return card_db, image_db
        logger.debug("Opening Databases")
        mtg_proxy_printer.carddb_migrations.migrate_card_database_location()
        card_db = mtg_proxy_printer.model.carddb.CardDatabase()
        image_db = mtg_proxy_printer.model.imagedb.ImageDatabase(parent=self)
        return card_db, image_db

    def _create_settings_window(
            self, language_model: QStringListModel, document: mtg_proxy_printer.model.document.Document,
            main_window: mtg_proxy_printer.ui.main_window.MainWindow):
        settings_window = mtg_proxy_printer.ui.settings_window.SettingsWindow(
            language_model, document, main_window)
        settings_window.request_run_async_task.connect(self.run_async_task)
        settings_window.custom_card_corner_style_changed.connect(document.on_custom_card_corner_style_changed)
        settings_window.document_settings_updated.connect(document.apply)
        settings_window.preferred_language_changed.connect(
            main_window.ui.central_widget.ui.add_card_widget.on_settings_preferred_language_changed)
        main_window.ui.action_show_settings.triggered.connect(
            partial(mtg_proxy_printer.ui.common.show_wizard_or_dialog, settings_window))
        return settings_window

    @Slot(AsyncTask)
    def run_async_task(self, task: AsyncTask):
        logger.debug(f"Received task to schedule: {task}")
        main_window = self.main_window
        task.ui_lock_acquire.connect(main_window.ui_lock_acquire, BlockingQueuedConnection)
        task.ui_lock_release.connect(main_window.ui_lock_release, BlockingQueuedConnection)
        task.error_occurred.connect(main_window.on_error_occurred)
        task.network_error_occurred.connect(main_window.on_network_error_occurred)
        if hasattr(task, "request_action"):
            task.request_action.connect(self.document.apply, BlockingQueuedConnection)
        if hasattr(task, "unknown_scryfall_ids_found"):
            task.unknown_scryfall_ids_found.connect(
                self.main_window.on_document_loading_found_unknown_scryfall_ids, BlockingQueuedConnection)
        if task.report_progress:
            main_window.progress_bar_manager.add_task(task)
        if isinstance(task, DatabaseImportTask):
            task.task_completed.connect(self.card_db.restart_transaction, BlockingQueuedConnection)
            task.task_completed.connect(self.card_db.card_data_updated, BlockingQueuedConnection)
        logger.debug(f"Starting task {task}")
        QThreadPool.globalInstance().start(AsyncTaskRunner(task))

    def _create_document_instance(
            self,
            card_db: mtg_proxy_printer.model.carddb.CardDatabase,
            image_db: mtg_proxy_printer.model.imagedb.ImageDatabase) -> mtg_proxy_printer.model.document.Document:
        document = mtg_proxy_printer.model.document.Document(card_db, image_db, self)
        document.request_run_async_task.connect(self.run_async_task)
        image_db.missing_image_obtained.connect(document.on_missing_image_obtained)
        return document

    def _create_language_model(self):
        preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        available = sorted({preferred_language, "en"})
        return QStringListModel(available, self)

    def _create_update_checker(self, args: Namespace) -> UpdateChecker:
        update_checker = UpdateChecker(self.card_db, args, self)
        update_checker.request_run_async_task.connect(self.run_async_task)
        update_checker.network_error_occurred.connect(self.main_window.on_network_error_occurred)
        update_checker.card_data_update_found.connect(self.main_window.show_card_data_update_available_message_box)
        update_checker.application_update_found.connect(self.main_window.show_application_update_available_message_box)
        return update_checker

    def _check_for_undecided_update_settings(self):
        section = settings.settings["update-checks"]
        if section.getboolean("check-for-application-updates") is None:
            logger.info("No user setting for application updates set. About to ask.")
            self.main_window.ask_user_about_application_update_policy()
        if section.getboolean("check-for-card-data-updates") is None:
            logger.info("No user setting for card data updates set. About to ask.")
            self.main_window.ask_user_about_card_data_update_policy()

    def _setup_translations(self):
        system_locale = QLocale.system()
        if configured_language := settings.settings["gui"]["language"]:
            locale = QLocale(configured_language)
        else:
            locale = system_locale
        logger.info(
            f"Loading localisations. System locale: {system_locale.name()}, selected locale: {locale.name()}. "
            f"Possible display languages are: {locale.uiLanguages()}")
        path = mtg_proxy_printer.ui.common.TRANSLATIONS_PATH
        logger.debug(f"Locale search path is '{path}'")
        self._load_translator(locale, "qtbase", QLibraryInfo.location(QLibraryInfo.LibraryPath.TranslationsPath))
        self._load_translator(locale, "mtgproxyprinter", path)

    def _load_translator(self, locale: QLocale, component: str, path: str):
        translator = QTranslator(self)
        if translator.load(locale, component, '_', path):
            logger.debug(f"{component} translation loaded successfully, installing it")
            self.installTranslator(translator)
        else:
            logger.warning(f"{component} translation failed to load. No translation available?")

    def _setup_icons(self):
        # The current icon theme name is empty by default, which causes the system-default theme, returned by
        # QIcon.fallbackThemeName() to be used.
        # On platforms without native icon theme support, both QIcon.themeName() and QIcon.fallbackThemeName()
        # return an empty string and no icons will load. These platforms require an explicit theme name set.

        # To test if the current platform has native icon theme support, check, if QIcon.fallbackThemeName() returns
        # a non-empty string. If it is empty, explicitly set the name of the internal icon theme. This will load the
        # internal icons.
        application_icon = mtg_proxy_printer.ui.common.load_icon("MTGPP_clean.png")
        self.setWindowIcon(application_icon)
        fallback_icon_theme = QIcon.fallbackThemeName()
        if not fallback_icon_theme:
            logger.info(
                "No native icon theme support or no system theme set, defaulting to internal icons."
            )
            if not mtg_proxy_printer.ui.common.HAS_COMPILED_RESOURCES:
                # If the compiled resources are available, the default search path ":/icons" is sufficient. Only append
                # the resources directory file system path, if directly running from the source distribution.
                theme_search_paths = QIcon.themeSearchPaths()
                theme_search_paths.append(mtg_proxy_printer.ui.common.ICON_PATH_PREFIX)
                QIcon.setThemeSearchPaths(theme_search_paths)
            QIcon.setThemeName("breeze")
        else:
            logger.debug(f"Using system-provided icon theme '{fallback_icon_theme}'")

    @Slot()
    def quit(self):
        logger.info("About to exit.")
        self.should_run = False
        self.main_window.hide()
        self.main_window.close()
        self.closeAllWindows()
        AsyncTaskRunner.cancel_all_tasks()
        logger.debug("All windows closed. Waiting for background threads to finish")
        pool = QThreadPool.globalInstance()
        pool.clear()
        pool.waitForDone(60000)
        logger.debug("Thread pool finished, calling quit()")
        super().quit()
