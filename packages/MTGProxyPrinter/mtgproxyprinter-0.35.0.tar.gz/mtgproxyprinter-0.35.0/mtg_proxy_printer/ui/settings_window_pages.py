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

from collections.abc import Sequence
import json
import logging
from functools import partial
import pathlib
import typing
from abc import abstractmethod

from PySide6.QtCore import Signal, Slot, QUrl, QStandardPaths, QStringListModel, Qt
from PySide6.QtGui import QDesktopServices, QStandardItem, QIcon, QColor
from PySide6.QtWidgets import QWidget, QCheckBox, QFileDialog, QMessageBox, QLineEdit, QDoubleSpinBox, \
    QColorDialog

import mtg_proxy_printer.app_dirs
import mtg_proxy_printer.settings
from mtg_proxy_printer.async_tasks.card_info_downloader import FileDownloadTask, FileStreamTask, DatabaseImportTask
from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingFilterUpdater
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.ui.common import highlight_widget, load_file, get_widget_background_color
from mtg_proxy_printer.units_and_sizes import OptStr, ConfigParser, unit_registry, Quantity
from mtg_proxy_printer.ui.page_config_container import PageConfigContainer

try:
    from mtg_proxy_printer.ui.generated.settings_window.debug_settings_page import Ui_DebugSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.decklist_import_settings_page \
        import Ui_DecklistImportSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.general_settings_page import Ui_GeneralSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.hide_printings_page import Ui_HidePrintingsPage
    from mtg_proxy_printer.ui.generated.settings_window.printer_settings_page import Ui_PrinterSettingsPage
    from mtg_proxy_printer.ui.generated.settings_window.export_settings_page import Ui_ExportSettingsPage
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_DebugSettingsPage = load_ui_from_file("settings_window/debug_settings_page")
    Ui_DecklistImportSettingsPage = load_ui_from_file("settings_window/decklist_import_settings_page")
    Ui_GeneralSettingsPage = load_ui_from_file("settings_window/general_settings_page")
    Ui_HidePrintingsPage = load_ui_from_file("settings_window/hide_printings_page")
    Ui_PrinterSettingsPage = load_ui_from_file("settings_window/printer_settings_page")
    Ui_ExportSettingsPage = load_ui_from_file("settings_window/export_settings_page")

CheckState = Qt.CheckState
bool_to_check_state: dict[bool | None, CheckState] = {
    True: CheckState.Checked,
    False: CheckState.Unchecked,
    None: CheckState.PartiallyChecked,
}
check_state_to_bool_str: dict[CheckState, str] = {v: str(k) for k, v in bool_to_check_state.items()}
QueuedConnection = Qt.ConnectionType.QueuedConnection
ItemDataRole = Qt.ItemDataRole
StandardLocation = QStandardPaths.StandardLocation
LocateOption = QStandardPaths.LocateOption
StandardButton = QMessageBox.StandardButton
logger = get_logger(__name__)
del get_logger
mm: Quantity = unit_registry.mm


class PageMetadata(typing.NamedTuple):
    text: str
    icon_name: OptStr
    tooltip: OptStr


class Page(QWidget):
    """The base class for settings page widgets. Defines the API used by the settings window"""

    def display_item(self) -> Sequence[QStandardItem]:
        """Returns a list model item for this page, used to represent the page in the settings page selection UI."""
        data = self.display_metadata()
        item = QStandardItem(data.text)
        if data.icon_name:
            item.setIcon(QIcon.fromTheme(data.icon_name))
        if data.tooltip:
            item.setToolTip(data.tooltip)
        size = item.sizeHint()
        size.setHeight(32)
        item.setSizeHint(size)
        return item,

    @abstractmethod
    def display_metadata(self) -> PageMetadata:
        """
        Returns the data shown by the page selection UI for this page. Must be overridden by subclasses.
        This is a method, and not a class attribute to allow runtime translation of UI strings.
        """
        return PageMetadata("FIXME: FILL DATA", None, "FIXME: FILL DATA")

    @abstractmethod
    def save(self):
        """Saves the GUI state into the global application settings"""
        pass

    @abstractmethod
    def load(self, settings: ConfigParser):
        """Loads the GUI state based on the given settings. This is used to load, reset, and revert settings."""
        pass

    @abstractmethod
    def highlight_differing_settings(self, settings: ConfigParser):
        """Highlights GUI widgets with a state different from the given settings"""
        pass

    def clear_highlight(self):
        """Clears all GUI widget highlights."""
        for item in self.findChildren(QWidget, options=Qt.FindChildOption.FindChildrenRecursively):  # type: QWidget
            item.setGraphicsEffect(None)


class DebugSettingsPage(Page):
    request_run_async_task = Signal(AsyncTask)

    def display_metadata(self) -> PageMetadata:
        return PageMetadata(
            self.tr("Debug settings"), None,
            self.tr("Things useful for investigating bugs in the application")
        )

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_DebugSettingsPage()
        ui.setupUi(self)
        self.request_run_async_task.connect(lambda _: ui.debug_download_card_data_as_file.setEnabled(False))
        ui.log_level_combo_box.addItems(map(logging.getLevelName, range(10, 60, 10)))
        url = QUrl("https://github.com/busimus/cutelog", QUrl.ParsingMode.StrictMode)
        ui.open_cutelog_website_button.clicked.connect(partial(QDesktopServices.openUrl, url))

    def load(self, settings: ConfigParser):
        section = settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            widget.setChecked(section.getboolean(setting))
        log_level_combo_box = self.ui.log_level_combo_box
        configured_level_index = log_level_combo_box.findText(section["log-level"])
        log_level_combo_box.setCurrentIndex(configured_level_index)

    def save(self):
        debug_section = mtg_proxy_printer.settings.settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            debug_section[setting] = str(widget.isChecked())
        debug_section["log-level"] = self.ui.log_level_combo_box.currentText()

    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["debug"]
        for widget, setting in self._get_debug_settings_checkbox_widgets():
            if widget.isChecked() != section.getboolean(setting):
                highlight_widget(widget)
        debug_combo_box = self.ui.log_level_combo_box
        if debug_combo_box.currentText() != section["log-level"]:
            highlight_widget(debug_combo_box)

    def _get_debug_settings_checkbox_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.enable_cutelog_integration, "cutelog-integration"),
            (ui.enable_write_log_file, "write-log-file")
        ]
        return widgets_with_settings

    @Slot()
    def on_open_debug_log_location_clicked(self):
        logger.debug("About to open the log directory using the default file manager.")
        log_dir = mtg_proxy_printer.app_dirs.data_directories.user_log_dir
        log_url = QUrl.fromLocalFile(log_dir)
        QDesktopServices.openUrl(log_url)

    @Slot()
    def on_debug_download_card_data_as_file_clicked(self):
        logger.debug("User about to download the card data from Scryfall to a file.")
        location = QFileDialog.getExistingDirectory(
            self, self.tr("Select download location"),
            QStandardPaths.locate(StandardLocation.DownloadLocation, "", LocateOption.LocateDirectory))
        if not location:
            logger.debug("User cancelled location selection. Not downloading.")
            return
        if not (path := pathlib.Path(location)).is_dir():
            logger.warning("User selected something that is not a directory. Aborting.")
            QMessageBox.critical(
                self, self.tr("Selected location is not a directory"),
                self.tr(
                    "Cannot write the card data at the given location, because it is not a directory:\n{location}"
                ).format(location=location),
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        logger.info(f"Download card data to file {path}")
        self.request_run_async_task.emit(FileDownloadTask(path))

    @Slot()
    def on_debug_import_card_data_from_file_clicked(self):
        logger.debug("User about to import card tata from a previously downloaded file.")
        location, _ = QFileDialog.getOpenFileName(
            self, self.tr("Import previously downloaded card data obtained from Scryfall"),
            QStandardPaths.locate(StandardLocation.DownloadLocation, "", LocateOption.LocateDirectory),
            self.tr("Scryfall card data (*.json, *.json.gz)"))
        logger.info(f"{location=}")
        if not location:
            logger.debug("User cancelled file selection. Not importing.")
            return
        if not (path := pathlib.Path(location)).is_file():
            logger.warning("User selected something that is not a file. Aborting.")
            QMessageBox.critical(
                self, self.tr("Selected location is not a file"),
                self.tr("Cannot find the selected file:\n{location}").format(location=location),
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        logger.info(f"Import card data from {path}")
        self.request_run_async_task.emit(data_source := FileStreamTask(path))
        self.request_run_async_task.emit(DatabaseImportTask(data_source))  # TODO: Pass the actually used carddb path


class DecklistImportSettingsPage(Page):

    def display_metadata(self) -> PageMetadata:
        return PageMetadata(self.tr("Deck list import"), "edit-download", self.tr("Configure the deck list importer"))

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_DecklistImportSettingsPage()
        ui.setupUi(self)

    @Slot()
    def on_deck_list_search_path_browse_button_clicked(self):
        logger.debug("User about to select a new default deck list search path.")
        if location := QFileDialog.getExistingDirectory(self, self.tr("Select default deck list search path")):
            logger.info("User selected a new default deck list search path.")
            self.ui.deck_list_search_path.setText(location)

    def load(self, settings: ConfigParser):
        section = settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            widget.setChecked(section.getboolean(setting))

        section = settings["default-filesystem-paths"]
        widgets_with_settings = self._get_save_path_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setText(section[setting])

    def save(self):
        section = mtg_proxy_printer.settings.settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            section[setting] = str(widget.isChecked())

        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        for widget, setting in self._get_save_path_settings_widgets():
            section[setting] = widget.text()

    def _get_checkbox_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.print_guessing_enable, "enable-print-guessing-by-default"),
            (ui.print_guessing_prefer_already_downloaded, "prefer-already-downloaded-images"),
            (ui.automatic_deck_list_translation_enable, "always-translate-deck-lists"),
            (ui.remove_basic_wastes_enable, "remove-basic-wastes"),
            (ui.remove_snow_basics_enable, "remove-snow-basics"),
            (ui.automatic_basics_removal_enable, "automatically-remove-basic-lands"),
        ]
        return widgets_with_settings

    def _get_save_path_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QLineEdit, str]] = [
            (ui.deck_list_search_path, "deck-list-search-path"),
        ]
        return widgets_with_settings

    def highlight_differing_settings(self, settings: ConfigParser):
        section = mtg_proxy_printer.settings.settings["decklist-import"]
        for widget, setting in self._get_checkbox_widgets():
            if widget.isChecked() != section.getboolean(setting):
                highlight_widget(widget)

        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        for widget, setting in self._get_save_path_settings_widgets():
            if widget.text() != section[setting]:
                highlight_widget(widget)


class GeneralSettingsPage(Page):

    custom_card_corner_style_changed = Signal()

    def display_metadata(self) -> PageMetadata:
        return PageMetadata(self.tr("General settings"), "configure", None)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_GeneralSettingsPage()
        ui.setupUi(self)
        self.set_language_model = ui.preferred_language_combo_box.setModel
        ui.add_card_widget_style_combo_box.addItem(self.tr("Horizontal layout"), "horizontal")
        ui.add_card_widget_style_combo_box.addItem(self.tr("Columnar layout"), "columnar")
        ui.add_card_widget_style_combo_box.addItem(self.tr("Tabbed layout"), "tabbed")
        progress: dict[str, int] = json.loads(load_file("translations/progress.json", self))
        for display_text, language_code in [
            (self.tr("System default"), ""),
            (self.tr("English (US) [{progress}%]"), "en_US"),
            (self.tr("German [{progress}%]"), "de"),
            (self.tr("French [{progress}%]"), "fr"),
        ]:
            display_text = display_text.format(progress=progress.get(language_code, ""))
            ui.application_language_combo_box.addItem(display_text, language_code)

    @Slot()
    def on_document_save_path_browse_button_clicked(self):
        logger.debug("User about to select a new default document save path.")
        if location := QFileDialog.getExistingDirectory(
                self, self.tr("Select default save location", "File picker title text")):
            logger.info("User selected a new default document save path.")
            self.ui.document_save_path.setText(location)

    @Slot()
    def on_custom_cards_search_path_browse_button_clicked(self):
        logger.debug("User about to select a new custom card search path.")
        if location := QFileDialog.getExistingDirectory(
                self, self.tr("Select custom card search path", "File picker title text")):
            logger.info("User selected a new custom card search path.")
            self.ui.custom_cards_search_path.setText(location)

    def load(self, settings: ConfigParser):
        self._load_look_and_feel_settings(settings)
        self._load_boolean_settings(settings)
        self._load_cards_settings(settings)
        self._load_path_settings(settings)

    def _load_look_and_feel_settings(self, settings: ConfigParser):
        ui = self.ui
        gui_section = settings["gui"]
        search_layout_index = ui.add_card_widget_style_combo_box.findData(gui_section["central-widget-layout"])
        ui.add_card_widget_style_combo_box.setCurrentIndex(search_layout_index)
        language_index = ui.application_language_combo_box.findData(gui_section["language"])
        ui.application_language_combo_box.setCurrentIndex(language_index)

    def _load_boolean_settings(self, settings: ConfigParser):
        for widget, section_name, setting in self._get_boolean_check_settings_widgets():
            section = settings[section_name]
            widget.setCheckState(bool_to_check_state[section.getboolean(setting)])

    def _load_cards_settings(self, settings: ConfigParser):
        section = settings["cards"]
        preferred_language_combo_box = self.ui.preferred_language_combo_box
        preferred_language = section.get("preferred-language")
        list_model: QStringListModel = preferred_language_combo_box.model()
        if not (known := list_model.stringList()) or preferred_language not in known:
            preferred_language_combo_box.addItem(preferred_language)
        preferred_language_combo_box.setCurrentIndex(self.get_index_for_language_code(preferred_language))

    def _load_path_settings(self, settings: ConfigParser):
        section = settings["default-filesystem-paths"]
        widgets_with_settings = self._get_path_settings_widgets()
        for widget, setting in widgets_with_settings:
            widget.setText(section[setting])

    def _get_boolean_check_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str, str]] = [
            (ui.check_application_updates_enabled, "update-checks", "check-for-application-updates"),
            (ui.check_card_data_updates_enabled, "update-checks", "check-for-card-data-updates"),
            (ui.automatically_add_opposing_faces, "cards", "automatically-add-opposing-faces"),
            (ui.gui_open_maximized, "gui", "gui-open-maximized"),
            (ui.wizards_open_maximized, "gui", "wizards-open-maximized"),
            (ui.custom_cards_force_round_corners, "cards", "custom-cards-force-round-corners"),
        ]
        return widgets_with_settings

    def get_index_for_language_code(self, language: str) -> int:
        languages = self.ui.preferred_language_combo_box.model().stringList()
        if language in languages:
            return languages.index(language)
        else:
            return languages.index("en")

    def save(self):
        corner_style_changed = \
            self.ui.custom_cards_force_round_corners.isChecked() \
            != mtg_proxy_printer.settings.settings["cards"].getboolean("custom-cards-force-round-corners")
        self._save_boolean_settings()
        self._save_look_and_feel_settings()
        self._save_cards_settings()
        self._save_path_settings()
        if corner_style_changed:
            logger.info("Custom card corner rounding style changed. Notifying the renderer to update the current view")
            self.custom_card_corner_style_changed.emit()

    def _save_boolean_settings(self):
        for widget, section_name, setting in self._get_boolean_check_settings_widgets():
            section = mtg_proxy_printer.settings.settings[section_name]
            section[setting] = check_state_to_bool_str[widget.checkState()]

    def _save_look_and_feel_settings(self):
        section = mtg_proxy_printer.settings.settings["gui"]
        section["central-widget-layout"] = self.ui.add_card_widget_style_combo_box.currentData(
            ItemDataRole.UserRole)
        section["language"] = self.ui.application_language_combo_box.currentData(
            ItemDataRole.UserRole)

    def _save_cards_settings(self):
        section = mtg_proxy_printer.settings.settings["cards"]
        section["preferred-language"] = self.ui.preferred_language_combo_box.currentText()

    def _save_path_settings(self):
        section = mtg_proxy_printer.settings.settings["default-filesystem-paths"]
        widgets_and_settings = self._get_path_settings_widgets()
        for widget, setting in widgets_and_settings:
            section[setting] = widget.text()

    def highlight_differing_settings(self, settings: ConfigParser):
        ui = self.ui
        for widget, section_name, setting in self._get_boolean_check_settings_widgets():
            section = settings[section_name]
            if section[setting] != check_state_to_bool_str[widget.checkState()]:
                highlight_widget(widget)

        section = settings["gui"]
        if section["central-widget-layout"] != ui.add_card_widget_style_combo_box.currentData(
                ItemDataRole.UserRole):
            highlight_widget(ui.add_card_widget_style_combo_box)
        if section["language"] != ui.application_language_combo_box.currentData(
                ItemDataRole.UserRole):
            highlight_widget(ui.application_language_combo_box)

        section = settings["cards"]
        if section["preferred-language"] != ui.preferred_language_combo_box.currentText():
            highlight_widget(ui.preferred_language_combo_box)

        section = settings["default-filesystem-paths"]
        widgets_and_settings = self._get_path_settings_widgets()
        for widget, setting in widgets_and_settings:
            if section[setting] != widget.text():
                highlight_widget(widget)

    def _get_path_settings_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QLineEdit, str]] = [
            (ui.document_save_path, "document-save-path"),
            (ui.custom_cards_search_path, "custom-cards-search-path")
        ]
        return widgets_with_settings


class HidePrintingsPage(Page):
    request_run_async_task = Signal(PrintingFilterUpdater)

    def display_metadata(self) -> PageMetadata:
        return PageMetadata(self.tr("Hide printings"), "view-hidden", self.tr("Hide unwanted printings"))

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_HidePrintingsPage()
        ui.setupUi(self)
        self.card_db = None

    def load(self, settings: ConfigParser):
        ui = self.ui
        section = settings["card-filter"]
        ui.set_filter_settings.setPlainText(section["hidden-sets"])
        ui.card_filter_general_settings.load_settings(section)
        ui.card_filter_format_settings.load_settings(section)

    def save(self):
        section = mtg_proxy_printer.settings.settings["card-filter"]
        ui = self.ui
        ui.card_filter_general_settings.save_settings(section)
        ui.card_filter_format_settings.save_settings(section)
        section["hidden-sets"] = ui.set_filter_settings.toPlainText()
        self.request_run_async_task.emit(PrintingFilterUpdater(self.card_db))

    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["card-filter"]
        ui = self.ui
        ui.card_filter_general_settings.highlight_differing_settings(settings)
        ui.card_filter_general_settings.highlight_differing_settings(settings)
        if section["hidden-sets"] != ui.set_filter_settings.toPlainText():
            highlight_widget(ui.set_filter_settings)


class DefaultDocumentLayoutSettingsPage(Page, PageConfigContainer):

    def display_metadata(self) -> PageMetadata:
        return PageMetadata(
            self.tr("Default document settings"), "document-properties",
            self.tr("Set the default document settings used for new documents,\n"
                    "like page size, margins, spacings, etc.")
        )

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.page_config_widget.setTitle(self.tr("Default settings for new documents"))

    @property
    def page_config_widget(self):
        return self.ui.page_config_widget

    def load(self, settings: ConfigParser):
        self.page_config_widget.load_document_settings_from_config(settings)

    def save(self):
        self.page_config_widget.save_document_settings_to_config()

    def highlight_differing_settings(self, settings: ConfigParser):
        self.page_config_widget.highlight_differing_settings(settings)


class PrinterSettingsPage(Page):
    def display_metadata(self) -> PageMetadata:
        return PageMetadata(self.tr("Printer settings"), "document-print", self.tr("Configure the printer"))

    def __init__(self, parent=None, flags=Qt.WindowType.Widget):
        super().__init__(parent, flags)
        self.ui = ui = Ui_PrinterSettingsPage()
        ui.setupUi(self)

    def _get_printer_settings_boolean_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.printer_use_borderless_printing, "borderless-printing"),
            (ui.landscape_workaround, "landscape-compatibility-workaround"),
        ]
        return widgets_with_settings

    def _get_printer_settings_length_widgets(self):
        ui = self.ui
        widgets_with_settings: list[tuple[QDoubleSpinBox, str]] = [
            (ui.horizontal_offset, "horizontal-offset"),
        ]
        return widgets_with_settings

    def load(self, settings: ConfigParser):
        section = settings["printer"]
        for checkbox, setting in self._get_printer_settings_boolean_widgets():
            checkbox.setChecked(section.getboolean(setting))
        for spinbox, setting in self._get_printer_settings_length_widgets():
            # TODO: Not fully unit-aware. Spinbox assumed in mm
            spinbox.setValue(section.get_quantity(setting).to("mm").magnitude)

    def save(self):
        section = mtg_proxy_printer.settings.settings["printer"]
        for checkbox, setting in self._get_printer_settings_boolean_widgets():
            section[setting] = str(checkbox.isChecked())
        for spinbox, setting in self._get_printer_settings_length_widgets():
            # TODO: Not fully unit-aware. Spinbox assumed in mm
            section[setting] = f"{spinbox.value()} mm"

    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["printer"]
        for checkbox, setting in self._get_printer_settings_boolean_widgets():
            if section.getboolean(setting) != checkbox.isChecked():
                highlight_widget(checkbox)
        for spinbox, setting in self._get_printer_settings_length_widgets():
            # TODO: Not fully unit-aware. Spinbox assumed in mm
            if spinbox.value()*mm != section.get_quantity(setting).to("mm"):
                highlight_widget(spinbox)


class ExportSettingsPage(Page):
    def display_metadata(self) -> PageMetadata:
        return PageMetadata(self.tr("Export settings"), "viewpdf", self.tr("Configure the PDF/PNG export"))

    def __init__(self, parent=None, flags=Qt.WindowType.Widget):
        super().__init__(parent, flags)
        self.ui = ui = Ui_ExportSettingsPage()
        ui.setupUi(self)
        self._get_png_background_color = partial(get_widget_background_color, ui.png_background_color)

    def load(self, settings: ConfigParser):
        ui = self.ui
        section = settings["export"]
        ui.pdf_page_count_limit.setValue(section.getint("pdf-page-count-limit"))
        ui.export_path.setText(section["export-path"])
        ui.landscape_workaround.setChecked(section.getboolean("landscape-compatibility-workaround"))
        self._set_png_background_color_display(QColor(section["png-background-color"]))

    def save(self):
        ui = self.ui
        section = mtg_proxy_printer.settings.settings["export"]
        section["pdf-page-count-limit"] = str(ui.pdf_page_count_limit.value())
        section["export-path"] = ui.export_path.text()
        section["landscape-compatibility-workaround"] = str(ui.landscape_workaround.isChecked())
        section["png-background-color"] = self._get_png_background_color().name(QColor.NameFormat.HexArgb)

    def highlight_differing_settings(self, settings: ConfigParser):
        ui = self.ui
        section = settings["export"]
        if section.getint("pdf-page-count-limit") != ui.pdf_page_count_limit.value():
            highlight_widget(ui.pdf_page_count_limit)
        if ui.export_path.text() != section["export-path"]:
            highlight_widget(ui.export_path)
        if ui.landscape_workaround.isChecked() != section.getboolean("landscape-compatibility-workaround"):
            highlight_widget(ui.landscape_workaround)
        if section["png-background-color"] != self._get_png_background_color().name(QColor.NameFormat.HexArgb):
            highlight_widget(ui.png_background_color)
            highlight_widget(ui.png_background_color_label)

    @Slot()
    def on_export_path_browse_button_clicked(self):
        logger.debug("User about to select a new default Export path.")
        if location := QFileDialog.getExistingDirectory(self, self.tr("Select default export location")):
            logger.info("User selected a new default export path.")
            self.ui.export_path.setText(location)
        else:
            logger.debug("User cancelled path selection")

    @Slot()
    def on_png_background_color_button_clicked(self):
        current_color = self._get_png_background_color()
        selected = QColorDialog.getColor(
            current_color, self, self.tr("Select PNG background color"),
            QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if selected.isValid():
            self._set_png_background_color_display(selected)

    def _set_png_background_color_display(self, color: QColor):
        # Can't use formatting, because embedded curly braces in the CSS style sheet
        style_sheet = "QLabel { background-color : {bg}}".replace("{bg}", color.name(QColor.NameFormat.HexArgb))
        self.ui.png_background_color.setStyleSheet(style_sheet)
