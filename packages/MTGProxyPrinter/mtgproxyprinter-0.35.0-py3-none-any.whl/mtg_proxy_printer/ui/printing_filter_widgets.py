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



import abc
from functools import partial

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGroupBox, QWidget, QCheckBox, QPushButton

from mtg_proxy_printer.units_and_sizes import ConfigParser, SectionProxy
from mtg_proxy_printer.ui.common import highlight_widget

try:
    from mtg_proxy_printer.ui.generated.settings_window.format_printing_filter import Ui_FormatPrintingFilter
    from mtg_proxy_printer.ui.generated.settings_window.general_printing_filter import Ui_GeneralPrintingFilter
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_FormatPrintingFilter = load_ui_from_file("settings_window/format_printing_filter")
    Ui_GeneralPrintingFilter = load_ui_from_file("settings_window/general_printing_filter")

ParsingMode = QUrl.ParsingMode


class AbstractPrintingFilter(QGroupBox):

    def load_settings(self, settings: SectionProxy):
        for widget, key in self._get_widgets_with_keys():
            widget.setChecked(settings.getboolean(key))

    def save_settings(self, settings: SectionProxy):
        for widget, key in self._get_widgets_with_keys():
            settings[key] = str(widget.isChecked())

    @staticmethod
    def view_query_on_scryfall(query: str):
        query_url = QUrl("https://scryfall.com/search", ParsingMode.StrictMode)
        query_url.setQuery(f"q={query}", ParsingMode.StrictMode)
        QDesktopServices.openUrl(query_url)

    @abc.abstractmethod
    def _get_widgets_with_keys(self) -> list[tuple[QCheckBox, str]]:
        pass

    @abc.abstractmethod
    def highlight_differing_settings(self, settings: ConfigParser):
        """Highlights GUI widgets with a state different from the given settings"""
        pass


class GeneralPrintingFilter(AbstractPrintingFilter):
    """
    Manages settings for all printing filters that are not related to bans in specific formats
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_GeneralPrintingFilter()
        ui.setupUi(self)
        ui.view_cards_depicting_racism.clicked.connect(
            partial(self.view_query_on_scryfall, "function:banned-due-to-racist-imagery"))
        ui.view_oversized_cards.clicked.connect(partial(self.view_query_on_scryfall, "is:oversized"))
        ui.view_white_bordered_cards.clicked.connect(partial(self.view_query_on_scryfall, "border:white"))
        ui.view_gold_bordered_cards.clicked.connect(partial(self.view_query_on_scryfall, "border:gold"))
        ui.view_borderless_cards.clicked.connect(partial(self.view_query_on_scryfall, "border:borderless"))
        ui.view_extended_art_cards.clicked.connect(partial(self.view_query_on_scryfall, "is:extended"))
        ui.view_funny_cards.clicked.connect(partial(self.view_query_on_scryfall, "is:funny"))
        ui.view_token.clicked.connect(partial(self.view_query_on_scryfall, "is:token"))
        ui.view_digital_cards.clicked.connect(partial(self.view_query_on_scryfall, "is:digital"))
        ui.view_reversible_cards.clicked.connect(partial(self.view_query_on_scryfall, "is:reversible"))
        ui.view_art_series_cards.clicked.connect(partial(self.view_query_on_scryfall, "layout:art-series"))

    def _get_widgets_with_keys(self) -> list[tuple[QCheckBox, str]]:
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.hide_cards_depicting_racism, "hide-cards-depicting-racism"),
            (ui.hide_cards_without_images, "hide-cards-without-images"),
            (ui.hide_oversized_cards, "hide-oversized-cards"),
            (ui.hide_white_bordered_cards, "hide-white-bordered"),
            (ui.hide_gold_bordered_cards, "hide-gold-bordered"),
            (ui.hide_borderless_cards, "hide-borderless"),
            (ui.hide_extended_art_cards, "hide-extended-art"),
            (ui.hide_funny_cards, "hide-funny-cards"),
            (ui.hide_token, "hide-token"),
            (ui.hide_digital_cards, "hide-digital-cards"),
            (ui.hide_reversible_cards, "hide-reversible-cards"),
            (ui.hide_art_series_cards, "hide-art-series-cards"),
        ]
        return widgets_with_settings

    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["card-filter"]
        for widget, setting in self._get_widgets_with_keys():
            if widget.isChecked() is not section.getboolean(setting):
                highlight_widget(widget)


class FormatPrintingFilter(AbstractPrintingFilter):
    """
    Manages printing filters for bans in specific formats. An enabled filter for a given format hides
    all cards that are banned in that format.
    """
    # TODO 1: Refactor to generate the checkbox list and button list from the format list in the settings
    # TODO 2: Write test that ensures that there is a bijection between settings keys and widgets
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui = Ui_FormatPrintingFilter()
        ui.setupUi(self)
        for _, key in self._get_widgets_with_keys():
            format_name = key.split("-")[-1]
            button: QPushButton = getattr(ui, f"view_banned_in_{format_name}")
            button.clicked.connect(
                partial(self.view_query_on_scryfall, f"banned:{format_name}")
            )

    def _get_widgets_with_keys(self) -> list[tuple[QCheckBox, str]]:
        ui = self.ui
        widgets_with_settings: list[tuple[QCheckBox, str]] = [
            (ui.hide_banned_in_brawl, "hide-banned-in-brawl"),
            (ui.hide_banned_in_commander, "hide-banned-in-commander"),
            (ui.hide_banned_in_historic, "hide-banned-in-historic"),
            (ui.hide_banned_in_legacy, "hide-banned-in-legacy"),
            (ui.hide_banned_in_modern, "hide-banned-in-modern"),
            (ui.hide_banned_in_oathbreaker, "hide-banned-in-oathbreaker"),
            (ui.hide_banned_in_pauper, "hide-banned-in-pauper"),
            (ui.hide_banned_in_penny, "hide-banned-in-penny"),
            (ui.hide_banned_in_pioneer, "hide-banned-in-pioneer"),
            (ui.hide_banned_in_standard, "hide-banned-in-standard"),
            (ui.hide_banned_in_vintage, "hide-banned-in-vintage"),
        ]
        return widgets_with_settings

    def highlight_differing_settings(self, settings: ConfigParser):
        section = settings["card-filter"]
        for widget, setting in self._get_widgets_with_keys():
            if widget.isChecked() is not section.getboolean(setting):
                highlight_widget(widget)
