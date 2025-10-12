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

from collections.abc import Callable

from PySide6.QtCore import QStringListModel, Signal, Qt, QItemSelectionModel, QEvent, QObject, QTimer
from PySide6.QtWidgets import QDialogButtonBox, QMessageBox, QWidget, QDialog
from PySide6.QtGui import QIcon, QStandardItemModel, QResizeEvent

import mtg_proxy_printer.app_dirs
from mtg_proxy_printer.async_tasks.base import AsyncTask
from mtg_proxy_printer.units_and_sizes import ConfigParser
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.document_controller import DocumentAction
from mtg_proxy_printer.document_controller.edit_document_settings import ActionEditDocumentSettings

import mtg_proxy_printer.settings
from mtg_proxy_printer.logger import get_logger
from mtg_proxy_printer.ui.settings_window_pages import Page, HidePrintingsPage

try:
    from mtg_proxy_printer.ui.generated.settings_window.settings_window import Ui_SettingsWindow
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_SettingsWindow = load_ui_from_file("settings_window/settings_window")


logger = get_logger(__name__)
del get_logger
MessageBoxButton = QMessageBox.StandardButton
DialogBoxButton = QDialogButtonBox.StandardButton
EventType = QEvent.Type
ItemDataRole = Qt.ItemDataRole
ClearAndSelect = QItemSelectionModel.SelectionFlag.ClearAndSelect
TALL_LAYOUT_THRESHOLD = 200

__all__ = [
    "SettingsWindow",
]


class HighlightDifferingSettingsHoverEventFilter(QObject):
    parent: Callable[[], "SettingsWindow"]

    def __init__(self, settings: ConfigParser, parent: "SettingsWindow"):
        super().__init__(parent)
        self.settings = settings

    def eventFilter(self, object_, event: QEvent):
        event_type = event.type()
        # This check avoids a crash during application shutdown
        if event_type not in {EventType.HoverEnter, EventType.HoverLeave}:
            return False
        parent = self.parent()
        if event_type == EventType.HoverEnter:
            parent.highlight_differing_settings(self.settings)
        elif event_type == EventType.HoverLeave:
            parent.clear_highlight()
        return False


class SettingsWindow(QDialog):
    """Implements the Settings window."""
    request_run_async_task = Signal(AsyncTask)
    saved = Signal()
    preferred_language_changed = Signal(str)
    document_settings_updated = Signal(DocumentAction)
    custom_card_corner_style_changed = Signal()

    def __init__(self, language_model: QStringListModel, document: Document, parent: QWidget = None):
        super().__init__(parent)
        self.language_model = language_model
        self.document = document
        self.ui = ui = Ui_SettingsWindow()
        ui.setupUi(self)
        ui.general_settings_page.custom_card_corner_style_changed.connect(self.custom_card_corner_style_changed)
        self.pages_model = self._setup_pages_model(ui)
        ui.general_settings_page.set_language_model(language_model)
        ui.default_document_layout_page.ui.page_config_preview_area.hide()
        # Delay the resize to the next event loop iteration
        ui.default_document_layout_page.ui.page_config_widget.ui.show_preview_button.clicked.connect(
            lambda: QTimer.singleShot(0, lambda: self._adapt_layout_to_size(self.size()))
        )
        self._setup_hide_printing_page(ui.hide_printings_page, document.card_db)
        ui.debug_settings_page.request_run_async_task.connect(self.request_run_async_task)
        self._setup_button_box()
        logger.info(f"Created {self.__class__.__name__} instance.")

    def _setup_pages_model(self, ui: Ui_SettingsWindow) -> QStandardItemModel:
        model = QStandardItemModel(self)
        # Create the model entries for each page, in the order they are stacked.
        pages: list[Page] = [ui.stacked_pages.widget(index) for index in range(ui.stacked_pages.count())]
        for page in pages:
            model.appendRow(page.display_item())
        # Set the models
        ui.page_selection_list_view.setModel(model)
        ui.page_selection_combo_box.setModel(model)
        ui.page_selection_list_view.setSelectionMode(ui.page_selection_list_view.SelectionMode.SingleSelection)
        first_page = model.index(0, 0)
        selection_model = ui.page_selection_list_view.selectionModel()
        selection_model.select(first_page, ClearAndSelect)
        # Connect the list view selection model and the combo box with the page stack
        selection_model.currentRowChanged.connect(lambda current, _: ui.stacked_pages.setCurrentIndex(current.row()))
        ui.page_selection_combo_box.currentIndexChanged.connect(ui.stacked_pages.setCurrentIndex)

        # Sync selections of both page list views
        selection_model.currentRowChanged.connect(
            lambda current, _: ui.page_selection_combo_box.setCurrentIndex(current.row()))
        ui.page_selection_combo_box.currentIndexChanged.connect(
            lambda row: selection_model.setCurrentIndex(model.index(row, 0), ClearAndSelect))

        return model

    def _setup_hide_printing_page(self, page: HidePrintingsPage, card_db):
        page.card_db = card_db
        page.request_run_async_task.connect(self.request_run_async_task)

    def _setup_button_box(self):
        button_box = self.ui.button_box

        restore_defaults = button_box.button(DialogBoxButton.RestoreDefaults)
        restore_defaults.clicked.connect(self.restore_defaults)
        restore_defaults.installEventFilter(
            HighlightDifferingSettingsHoverEventFilter(mtg_proxy_printer.settings.DEFAULT_SETTINGS, self))

        reset = button_box.button(DialogBoxButton.Reset)
        reset.clicked.connect(self.reset)
        reset.installEventFilter(
            HighlightDifferingSettingsHoverEventFilter(mtg_proxy_printer.settings.settings, self))

        buttons_with_icons = [
            (DialogBoxButton.Reset, "edit-undo"),
            (DialogBoxButton.Save, "document-save"),
            (DialogBoxButton.Cancel, "dialog-cancel"),
            (DialogBoxButton.RestoreDefaults, "document-revert"),
        ]
        for role, icon in buttons_with_icons:
            button = button_box.button(role)
            if button.icon().isNull():
                button.setIcon(QIcon.fromTheme(icon))

    def show(self):
        logger.info("Show the settings window.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        self._adapt_layout_to_size(self.size())
        super().show()

    def resizeEvent(self, a0: QResizeEvent):
        self._adapt_layout_to_size(a0.size())
        super().resizeEvent(a0)

    def highlight_differing_settings(self, setting: ConfigParser):
        for page in self._get_pages():
            page.highlight_differing_settings(setting)

    def clear_highlight(self):
        for page in self._get_pages():
            page.clear_highlight()

    def _adapt_layout_to_size(self, size):
        ui = self.ui
        # The minimum size hint contains the minimum size the widget can occupy without clipping. If there is less than
        # TALL_LAYOUT_THRESHOLD pixels available for the page list, switch to a drop-down based layout
        min_width = ui.stacked_pages.minimumSizeHint().width()
        is_narrow = size.width() < TALL_LAYOUT_THRESHOLD + min_width
        ui.page_selection_list_view.setHidden(is_narrow)
        ui.page_selection_combo_box.setVisible(is_narrow)

    def _get_pages(self) -> list[Page]:
        ui = self.ui
        return [ui.stacked_pages.widget(index) for index in range(ui.stacked_pages.count())]

    def load_settings(self, settings: ConfigParser):
        logger.debug("Loading the settings")
        for page in self._get_pages():
            page.load(settings)
        logger.debug("Finished loading settings")

    def accept(self):
        """Automatically called when the user hits the "Save" button."""
        logger.info("User wants to save the settings.")
        old_preferred_language = mtg_proxy_printer.settings.settings["cards"]["preferred-language"]
        new_preferred_language = self.ui.general_settings_page.ui.preferred_language_combo_box.currentText()
        if old_preferred_language != new_preferred_language:
            self.preferred_language_changed.emit(new_preferred_language)
        current_document_layout = self.document.page_layout
        new_default_layout = self.ui.default_document_layout_page.ui.page_config_widget.page_layout
        if current_document_layout != new_default_layout and QMessageBox.question(
                self, self.tr("Apply settings to the current document?"),
                self.tr("The new default settings differ from the settings used by the current document.\n"
                        "Apply the new settings to the current document?"),
                MessageBoxButton.Yes | MessageBoxButton.No, MessageBoxButton.Yes
        ) == MessageBoxButton.Yes:
            logger.info("User applies changed document settings to the current document")
            self.document_settings_updated.emit(ActionEditDocumentSettings(new_default_layout))
        self.save()
        super().accept()

    def reset(self):
        logger.debug("User clicked the reset button.")
        scope_question = QMessageBox(
            QMessageBox.Icon.Question,
            self.tr("Reset unsaved changes?"),
            self.tr("Reset unsaved changes on the current page or on all pages?"),
            MessageBoxButton.YesToAll | MessageBoxButton.Yes | MessageBoxButton.Cancel,
            self)
        scope_question.button(MessageBoxButton.YesToAll).setText(self.tr("Reset everything"))
        scope_question.button(MessageBoxButton.Yes).setText(self.tr("Reset current page"))
        if (result := scope_question.exec()) == MessageBoxButton.YesToAll:
            logger.info("User resets changes made on all pages.")
            self.load_settings(mtg_proxy_printer.settings.settings)
            self.clear_highlight()
        elif result == MessageBoxButton.Yes:
            logger.info("User resets changes made on the current page.")
            self.ui.stacked_pages.currentWidget().load(mtg_proxy_printer.settings.settings)
            self.clear_highlight()

    def reject(self):
        """Automatically called when the user hits the "Cancel" button or closes the settings window."""
        logger.info("User closes the settings dialog. This will reset any made changes.")
        self.load_settings(mtg_proxy_printer.settings.settings)
        super().reject()

    def save(self):
        logger.info("User saves the configuration to disk.")
        for page in self._get_pages():
            page.save()
        logger.debug("Settings read from UI widgets, about to write the configuration to disk.")
        mtg_proxy_printer.settings.write_settings_to_file()
        self.saved.emit()
        logger.debug("Save finished.")

    def restore_defaults(self):
        logger.debug("User clicked the 'Restore Defaults' button.")
        scope_question = QMessageBox(
            QMessageBox.Icon.Question,
            self.tr("Restore defaults for the current page or everything?"),
            self.tr("Restore the settings on the current page or on all pages to their default values?"),
            MessageBoxButton.YesToAll | MessageBoxButton.Yes | MessageBoxButton.Cancel,
            self)
        scope_question.button(MessageBoxButton.YesToAll).setText(self.tr("Restore everything"))
        scope_question.button(MessageBoxButton.Yes).setText(self.tr("Restore current page"))
        if (result := scope_question.exec()) == MessageBoxButton.YesToAll:
            logger.info("User reverts all pages to their default values.")
            self.load_settings(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
            self.clear_highlight()
        elif result == MessageBoxButton.Yes:
            logger.info("User reverts the current page to the default values.")
            self.ui.stacked_pages.currentWidget().load(mtg_proxy_printer.settings.DEFAULT_SETTINGS)
            self.clear_highlight()
        logger.debug("Loaded DEFAULT_SETTINGS.")
