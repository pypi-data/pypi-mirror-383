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


import functools
import itertools
import typing

from PySide6.QtCore import QObject

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.decklist_parser.common import CardCounter
    from mtg_proxy_printer.model.document import Document


from ._interface import ActionList, DocumentAction, Self, IllegalStateError
from .page_actions import ActionRemovePage
from .card_actions import ActionAddCard
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

__all__ = [
    "ActionImportDeckList",
]


class ActionImportDeckList(DocumentAction):

    COMPARISON_ATTRIBUTES = ["cards", "clear_document", "actions"]

    def __init__(self, cards: "CardCounter", clear_document: bool, parent: QObject = None):
        super().__init__(parent)
        self.cards = cards
        self.clear_document = clear_document
        self.actions: ActionList = []

    def apply(self, document: "Document") -> Self:
        logger.info(f"About to apply {self.__class__.__name__}")
        if self.actions:
            raise IllegalStateError("Cannot apply action twice")
        if self.clear_document:
            self.actions.append(
                ActionRemovePage(0, document.rowCount()).apply(document)
            )
        active_page = document.find_page_list_index(document.currently_edited_page)
        for action in itertools.starmap(ActionAddCard, self.cards.items()):
            action.target_page = active_page
            self.actions.append(action.apply(document))
            if action.first_added_page is not None:
                active_page = action.first_added_page
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        for action in reversed(self.actions):
            action.undo(document)
        self.actions.clear()
        return super().undo(document)

    def card_count(self) -> int:
        """Returns the number of cards added by this action"""
        return sum(self.cards.values())

    @functools.cached_property
    def as_str(self):
        count = self.card_count()
        if self.clear_document:
            return self.tr(
                "Replace document with imported deck list containing %n card(s)",
                "Undo/redo tooltip text. Option to delete the current document enabled.", count)
        else:
            return self.tr(
                "Import a deck list containing %n card(s)",
                "Undo/redo tooltip text. Option to delete the current document disabled.", count)
