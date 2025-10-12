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
import functools
import itertools
import math
import typing

from PySide6.QtCore import QObject

if typing.TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.card import Card, AnyCardType
from mtg_proxy_printer.model.document_page import Page
from mtg_proxy_printer.natsort import to_list_of_ranges
from ._interface import DocumentAction, IllegalStateError, Self, split_iterable
from .page_actions import ActionNewPage, ActionRemovePage
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionAddCard",
    "ActionRemoveCards",
]
T = typing.TypeVar("T")


class ActionAddCard(DocumentAction):
    """
    Add an amount of copies of a card to a document page. If the count exceeds the available space on that page,
    distribute the remainder across free spots on later pages or append new pages to the document end.
    """

    COMPARISON_ATTRIBUTES = ["card", "count", "added_new_pages", "added_cards_to_existing_pages"]

    def __init__(self, card: AnyCardType, count: int = 1, *, target_page: int = None, parent: QObject = None):
        super().__init__(parent)
        self.target_page = target_page
        self.card = card
        self.count = count
        self.added_new_pages: int = 0
        self.first_added_page: int | None = None
        self.added_cards_to_existing_pages: list[tuple[int, int]] = []

    def apply(self, document: "Document") -> Self:
        """
        Adds the given card count times to the currently edited page. If count is greater than the number of
        free slots on that page, add the remaining card copies to free slots in subsequent pages.
        If that is insufficient, add and fill new pages at the document end to fulfil the required copies.
        """
        copies = self.count  # Copy the count, because the value is mutated
        page_capacity_for_card = document.page_layout.compute_page_card_capacity(self.card.requested_page_type())
        current_page_position = self.target_page if self.target_page is not None \
            else document.find_page_list_index(document.currently_edited_page)
        page = document.pages[current_page_position]
        if len(page) < page_capacity_for_card and page.accepts_card(self.card):
            copies -= (added_cards := self.add_card_to_page(document, current_page_position, self.card, copies))
            if added_cards:
                self.added_cards_to_existing_pages.append((current_page_position, added_cards))
            logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
        current_page_position += 1
        while copies > 0 and current_page_position < document.rowCount():
            page = document.pages[current_page_position]
            if page.accepts_card(self.card):
                copies -= (added_cards := self.add_card_to_page(document, current_page_position, self.card, copies))
                if added_cards:
                    self.added_cards_to_existing_pages.append((current_page_position, added_cards))
                logger.debug(f"Added {added_cards} cards to page {current_page_position}. Remaining to add: {copies}")
            current_page_position += 1
        if copies > 0:
            self.added_new_pages = math.ceil(copies/page_capacity_for_card)
            logger.debug(
                f"No further empty slots found. Appending {self.added_new_pages} new pages to the document, "
                f"to fit the remaining {copies} copies.")
            content = split_iterable(itertools.repeat(self.card, copies), page_capacity_for_card)
            ActionNewPage(count=self.added_new_pages, content=content).apply(document)
            self.first_added_page = current_page_position
        return super().apply(document)

    @staticmethod
    def add_card_to_page(document: "Document", page_number: int, card: Card, count: int = 1) -> int:
        """
        Adds the given card up to count times to the given page. Returns the number of cards actually added.
        Only adds cards up to the page capacity, so may add less than count cards, if that would overflow the page.
        """
        page_index = document.index(page_number, 0)
        page = document.pages[page_number]
        page_card_count = len(page)
        # Not using the current page’s page type, because UNDETERMINED pages overestimate the capacity when adding
        # oversized pages. Using the requested page type from the Card object is fine, because this method is only
        # called, if the given card fits on the given page.
        page_capacity = document.page_layout.compute_page_card_capacity(card.requested_page_type())
        first_index, last_index = page_card_count, page_card_count + count - 1
        if last_index >= page_capacity:
            last_index = page_capacity - 1
        cards_inserted = last_index - first_index + 1
        if not cards_inserted:
            logger.debug(f"Trying to add {count} cards into full page {page_number}. Doing nothing")
            return 0
        document.beginInsertRows(page_index, first_index, last_index)
        old_page_type = page.page_type()
        page += (card for _ in range(cards_inserted))
        logger.debug(f"After insert, page contains {len(page)} images.")
        document.endInsertRows()
        if old_page_type != (new_page_type := page.page_type()):
            logger.debug(f"Page type of page {page_number} changed from {old_page_type} to {new_page_type}")
            document.page_type_changed.emit(page_index)
        logger.debug(f'Added {cards_inserted} × "{card.name}" to page {page_number}')
        return cards_inserted

    def undo(self, document: "Document") -> Self:
        if not self.added_new_pages and not self.added_cards_to_existing_pages:
            raise IllegalStateError("No cards added to undo")
        if self.added_new_pages:  # Drop all appended pages, implicitly removing all cards on them
            ActionRemovePage(document.rowCount() - self.added_new_pages, count=self.added_new_pages).apply(document)
        for page_number, count in self.added_cards_to_existing_pages:
            cards_on_page = len(document.pages[page_number])
            # Cards are always appended when filling a page via this action. So remove the last count cards will remove
            # the cards added during apply().
            ActionRemoveCards(
                range(cards_on_page-count, cards_on_page),
                page_number
            ).apply(document)

        self.added_new_pages = self.first_added_page = 0
        self.added_cards_to_existing_pages.clear()
        return super().undo(document)

    @functools.cached_property
    def as_str(self):
        n = 1
        if len(self.added_cards_to_existing_pages) == 1 and not self.first_added_page:
            # Cards added to a single existing page
            target = self.added_cards_to_existing_pages[0][0]+1
        elif self.first_added_page and not self.added_cards_to_existing_pages:
            # Cards added to a single new page
            target = self.first_added_page+1
        else:
            # Cards added to multiple existing and/or new pages
            existing_pages = ((page + 1) for page, _ in self.added_cards_to_existing_pages)
            new_pages = range(self.first_added_page+1, self.first_added_page+self.added_new_pages+1) \
                if self.first_added_page else []
            all_pages = list(itertools.chain(existing_pages, new_pages))
            n = len(all_pages)
            page_ranges = to_list_of_ranges(all_pages)
            # Human-readable representation: pages are comma-separated,
            # with consecutive values collapsed into hyphen-separated ranges like lower-upper
            target = ", ".join(itertools.starmap(self._format_number_range, page_ranges))
        return self.tr(
            "Add {count} × {card_display_string} to page {target}",
            "Undo/redo tooltip text. Plural form refers to {target}, not {count}. "
            "{target} can be multiple ranges of multiple pages each", n
        ).format(count=self.count, card_display_string=self.card.display_string(), target=target)


class ActionRemoveCards(DocumentAction):
    """
    Deletes one or more cards from a page.
    The cards are given as a sorted, inclusive sequence of ascending array indices.
    """

    COMPARISON_ATTRIBUTES = ["card_ranges_to_remove", "page_number", "removed_cards"]

    def __init__(self, cards_to_remove: Sequence[int], page_number: int = None, parent: QObject = None):
        if not cards_to_remove:
            raise ValueError("Parameter cards_to_remove must not be empty")
        super().__init__(parent)
        # The source of the input row sequence is a Qt multi-selection, which is unordered.
        # The individual selections are ordered, but the selection groups are not. To not break the algorithm,
        # if the user selects cards from bottom to top, the rows have to be sorted.
        self.card_ranges_to_remove = to_list_of_ranges(cards_to_remove)
        self.page_number = page_number
        self.removed_cards: list[Page] = []

    def apply(self, document: "Document") -> Self:
        if self.page_number is None:
            self.page_number = document.find_page_list_index(document.currently_edited_page)
        page_index = document.index(self.page_number, 0)
        page = document.pages[self.page_number]
        old_page_type = page.page_type()
        for lower, upper in reversed(self.card_ranges_to_remove):
            document.beginRemoveRows(page_index, lower, upper)
            self.removed_cards.append(page[lower:upper+1])
            del page[lower:upper+1]
            document.endRemoveRows()
        self.removed_cards.reverse()
        if page.page_type() != old_page_type:
            document.page_type_changed.emit(document.index(self.page_number, 0))
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        if self.page_number is None:
            raise IllegalStateError("page_number is None")
        page = document.pages[self.page_number]
        page_index = document.index(self.page_number, 0)
        for (begin, end), cards in zip(self.card_ranges_to_remove, self.removed_cards):  # type: (int, int), Page
            document.beginInsertRows(page_index, begin, end)
            for card in reversed(cards):
                page.insert(begin, card)
            document.endInsertRows()
        self.removed_cards.clear()
        return super().undo(document)

    @functools.cached_property
    def as_str(self):
        card_count = sum(upper-lower+1 for lower, upper in self.card_ranges_to_remove)
        page_number = self.page_number+1
        return self.tr(
            "Remove %n card(s) from page {page_number}",
            "Undo/redo tooltip text", card_count
        ).format(page_number=page_number)
