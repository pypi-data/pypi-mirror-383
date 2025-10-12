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


from collections.abc import Iterable
import functools
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.document_page import Page
from mtg_proxy_printer.model.card import AnyCardType
from ._interface import DocumentAction, IllegalStateError, Self
from mtg_proxy_printer.logger import get_logger

logger = get_logger(__name__)
del get_logger
__all__ = [
    "ActionNewPage",
    "ActionRemovePage",
]
ContentType = list[Iterable[AnyCardType]]


class ActionNewPage(DocumentAction):
    """
    Insert count new, empty pages at the given index or at the document end.
    If the position is None, append the page at the end.
    Otherwise, insert it at the given index, pushing the page at and after the position behind the new pages.
    Positions are clamped into the range [0, page_count].

    Page count defaults to 1.
    If content is given, it must be a list[list[AnyCardType]], with length equal to count.
    Individual lists in content may be empty. If content is given, the cards in content are placed on the
    created pages in the order given.
    """

    COMPARISON_ATTRIBUTES = ["position", "count", "content",]

    def __init__(self, position: int = None, *, count: int = 1, content: ContentType = None, parent: QObject = None):
        if count <= 0:
            raise ValueError(f"Invalid page count given: {count}")
        super().__init__(parent)
        self.position = position
        self.count = count
        self.content: ContentType = content or [[]] * count
        self._validate_content_does_not_create_mixed_pages(self.content)
        if len(self.content) != count:
            raise ValueError("Page content given, but not enough to supply all pages")

    def apply(self, document: "Document") -> Self:
        self.position = document.rowCount() if self.position is None \
            else max(0, min(self.position, document.rowCount()))
        document.beginInsertRows(document.INVALID_INDEX, self.position, self.position+self.count-1)
        document.pages[self.position:self.position] = map(Page, self.content)
        document.recreate_page_index_cache()
        document.endInsertRows()
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        if self.position is None:
            raise IllegalStateError("Page position not set")
        ActionRemovePage(self.position, self.count).apply(document)
        return super().undo(document)

    @functools.cached_property
    def as_str(self):
        count = self.count
        pages = self._format_number_range(self.position+1, self.position+count)
        # Implementation note: pylupdate5 does not support passing object attributes as parameters.
        # Passing "self.count", instead of "count" breaks the string extraction.
        result = self.tr(
            "Add page(s) {pages}",
            "Undo/redo tooltip text. Translations should drop the %n placeholder", count
        ).format(pages=pages)
        return result

    @staticmethod
    def _validate_content_does_not_create_mixed_pages(content: ContentType):
        for index, page in enumerate(content):
            types_on_page = {card.requested_page_type() for card in page}
            if len(types_on_page) > 1:
                raise ValueError(f"Mixed-size content on page {index}. Requested: {types_on_page}, cards: {page}")


class ActionRemovePage(DocumentAction):
    """
    Delete count pages starting at the given index.
    If position is None, start deleting at the current page instead.
    """

    COMPARISON_ATTRIBUTES = ["position", "count", "removed_all_pages", "currently_edited_page", "removed_pages"]

    def __init__(self, position: int = None, count: int = 1, parent: QObject = None):
        super().__init__(parent)
        self.position = position
        self.count = count
        self.removed_pages: list[Page] = []
        self.currently_edited_page: Page | None = None  # Set, if the currently edited page is removed
        self.removed_all_pages: bool = False

    def apply(self, document: "Document") -> Self:
        self.position = first_index = self.position if self.position is not None \
            else document.find_page_list_index(document.currently_edited_page)
        last_index = first_index + self.count - 1
        logger.debug(f"Removing pages {first_index} to {last_index}. {document.rowCount()=}")
        self.removed_pages[:] = document.pages[first_index:last_index+1]
        # Note: Can not use "currently_edited_page in removed_pages", because the in operator does not check for
        # object identity, which is required here.
        currently_edited_page_removed = \
            first_index <= document.find_page_list_index(document.currently_edited_page) <= last_index
        if currently_edited_page_removed:
            self.currently_edited_page = document.currently_edited_page
        document.beginRemoveRows(document.INVALID_INDEX, first_index, last_index)
        del document.pages[first_index:last_index+1]
        document.recreate_page_index_cache()
        document.endRemoveRows()
        if not document.pages:
            self.removed_all_pages = True
            ActionNewPage().apply(document)
            document.set_currently_edited_page(document.pages[0])
        elif currently_edited_page_removed:
            newly_selected_page = min(first_index, document.rowCount()-1)
            logger.debug(f"Currently edited page is removed, switching to page {newly_selected_page}")
            # Since the page list is non-empty, there is always a page to select.
            # Choose the first after the removed range or the last, whichever comes first.
            document.set_currently_edited_page(document.pages[newly_selected_page])
        return super().apply(document)

    def undo(self, document: "Document") -> Self:
        start = self.position
        if start is None:
            raise IllegalStateError("Cannot undo page removal without location to restore")
        end = start + len(self.removed_pages) - 1
        document.beginInsertRows(document.INVALID_INDEX, start, end)
        if start == document.rowCount():
            self._append_pages(document, start)
        else:
            self._insert_pages(document, start)
        document.endInsertRows()
        if self.currently_edited_page is not None:
            document.set_currently_edited_page(self.currently_edited_page)
        if self.removed_all_pages:
            # The Action replaced the whole document with an empty page during apply().
            # To undo the creation of the empty replacement page, delete the now obsolete page
            page_to_remove = end + 1
            document.beginRemoveRows(document.INVALID_INDEX, page_to_remove, page_to_remove)
            del document.page_index_cache[id(document.pages[page_to_remove])]
            del document.pages[page_to_remove]
            document.endRemoveRows()
        # Clear state gathered during apply()
        self.removed_pages.clear()
        self.currently_edited_page = None
        self.removed_all_pages = False
        return super().undo(document)

    def _append_pages(self, document: "Document", start: int):
        document.pages += self.removed_pages
        document.page_index_cache.update(
            (id(page), index) for index, page in enumerate(self.removed_pages, start=start)
        )

    def _insert_pages(self, document: "Document", start: int):
        for index, page in enumerate(self.removed_pages, start=start):
            document.pages.insert(index, page)
        document.recreate_page_index_cache()

    @functools.cached_property
    def as_str(self):
        cards_removed = sum(map(len, self.removed_pages))
        count = self.count
        formatted_pages = self._format_number_range(self.position+1, self.position+count)
        formatted_card_count = self.tr(
            "%n card(s) total",
            "Undo/redo tooltip text. The total number of cards removed. Used as {formatted_card_count}", cards_removed
        )
        # Implementation note: pylupdate5 does not support passing object attributes as parameters.
        # Passing "self.count", instead of "count" breaks the string extraction.
        result = self.tr(
            "Remove page(s) {formatted_pages} containing {formatted_card_count}",
            "Undo/redo tooltip text", count
        ).format(formatted_pages=formatted_pages, formatted_card_count=formatted_card_count)
        return result
