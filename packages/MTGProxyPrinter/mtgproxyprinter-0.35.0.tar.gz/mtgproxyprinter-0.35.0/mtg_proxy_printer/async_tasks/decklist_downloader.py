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


"""
This module is responsible for downloading deck lists from a known list of deckbuilder websites.
"""
import abc
import collections
from collections.abc import Iterable
import csv
import html.parser
import io
import urllib.parse
from io import StringIO
import platform
import re
from typing import Type, Counter, Any, Union

import ijson
from PySide6.QtGui import QValidator

from mtg_proxy_printer.async_tasks.downloader_base import DownloaderBase
from mtg_proxy_printer.decklist_parser.common import ParserBase
from mtg_proxy_printer.decklist_parser.csv_parsers import ScryfallCSVParser, TappedOutCSVParser
from mtg_proxy_printer.decklist_parser.re_parsers import MTGArenaParser, MagicWorkstationDeckDataFormatParser, \
    XMageParser
from mtg_proxy_printer.logger import get_logger
logger = get_logger(__name__)
del get_logger

Counter = collections.Counter if int(platform.python_version_tuple()[1]) >= 9 else Counter

JSONType = dict[str, Union[str, int, list, "JSONType", float, bool]]
JSONKeyValueType = Iterable[tuple[str, JSONType]]
HTMLAttributeType = list[tuple[str, str | None]]
State = QValidator.State


class IsIdentifyingDeckUrlValidator(QValidator):
    """
    Validator that checks, if the given string is a valid URL prefix pointing to a deck on a known deck
    building website.
    If this validator passes, at least one downloader class is able to fetch a deck list from the given input string.
    """

    def validate(self, input_string: str, pos: int = 0) -> tuple[QValidator.State, str, int]:
        logger.debug(f"Validating input: {input_string}")
        for downloader_class in AVAILABLE_DOWNLOADERS.values():
            if downloader_class.DECKLIST_PATH_RE.match(input_string) is not None:
                logger.debug(f"Input is valid URL for {downloader_class.APPLICABLE_WEBSITES}")
                return State.Acceptable, input_string, pos
        return State.Intermediate, input_string, pos


class DecklistDownloader(DownloaderBase):
    DECKLIST_PATH_RE = re.compile(r"")  # Defines the acceptable download URLs. Set by subclasses
    PARSER_CLASS: Type[ParserBase] = None  # The parser class used to parse the output deck list.
    APPLICABLE_WEBSITES: str = ""  # Name of compatible websites for display purposes. Set by subclasses

    def download(self, decklist_url: str) -> str:
        """
        Fetches the decklist from the given URL.
        The base class handles the download including transparent decompression, and performs post-processing steps:
        Replacing Windows-style line endings \r\n with plain \n newlines, and decoding bytes assuming utf-8 input
        """
        logger.info(f"About to fetch deck list from {decklist_url}")
        download_url = self.map_to_download_url(decklist_url)
        logger.debug(f"Obtained download URL: {download_url}")
        data, monitor = self.read_from_url(download_url, "Downloading deck list:")
        with data, monitor:
            raw_data = data.read()
        deck_list = self.post_process(raw_data)
        line_count = deck_list.count('\n')
        logger.debug(f"Obtained deck list containing {line_count} lines.")
        return deck_list

    @staticmethod
    def post_process(data: bytes) -> str:
        """
        Takes the raw, downloaded data and post-processes them into a user-presentable string.
        Default replaces \r\n to \n and decodes bytes to str using utf-8 encoding
        """
        deck_list = data.replace(b"\r\n", b"\n")
        deck_list = deck_list.decode("utf-8")
        return deck_list

    def map_to_download_url(self, decklist_url: str) -> str:
        """
        Takes a URL to a deck list and returns a download URL. By default, returns the identity.
        Can be overridden to perform site-specific mappings from front-end URL to backend API or similar.
        """
        return decklist_url


class ScryfallDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"(https://scryfall\.com/@\w+/decks/(?P<uuid>[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12})/?)|"
        r"(https://api.scryfall.com/cards/search?.*(?P<search_param>q=.+).*)"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "Scryfall (scryfall.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        if uuid := match.group("uuid"):
            return f"https://api.scryfall.com/decks/{uuid}/export/csv"
        else:
            search_parameters = decklist_url.split("search?", 1)[1]
            parsed_parameters = dict(urllib.parse.parse_qsl(search_parameters))
            parsed_parameters["format"] = "csv"  # Enforce CSV format
            parsed_parameters["include_multilingual"] = "true"  # Ensure that non-English cards can be found
            parsed_parameters["include_extras"] = "true"  # Ensure that non-traditional cards can be found
            quoted_parameters = "&".join(
                f"{key}={urllib.parse.quote(value)}"
                for key, value in parsed_parameters.items())
            return f"https://api.scryfall.com/cards/search?{quoted_parameters}"


class MTGAZoneHTMLParser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.deck: list[str] = []

    def handle_starttag(self, tag: str, attrs: HTMLAttributeType) -> None:
        attrs = dict(attrs)
        if tag == "div" and attrs.get("class", "").strip().lower() == "card":
            self.deck.append(f"{attrs['data-quantity']} {attrs['data-name']}")


class MTGAZoneDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://mtgazone\.com/deck/.+"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "MTG Arena Zone (mtgazone.com)"

    def post_process(self, data: bytes) -> str:
        decoded = super().post_process(data)
        parser = MTGAZoneHTMLParser()
        parser.feed(decoded)
        parser.close()
        deck = "\n".join(parser.deck)
        return deck


class MTGGoldfishDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?mtggoldfish\.com/"
        r"(deck(/download)?/(?P<deck_id>\d+)|archetype/(?P<archetype_name>[-_\w]+))"
        r"([#?].*)?$"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "MTGGoldfish (mtggoldfish.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        deck_id = match.group("deck_id") or self._fetch_deck_id_of_archetype_link(decklist_url)
        url = f"https://www.mtggoldfish.com/deck/download/{deck_id}?type=arena"
        return url

    def _fetch_deck_id_of_archetype_link(self, decklist_url: str):
        logger.info("Got an archetype link. Downloading the website to obtain the deck id")
        downloader, monitor = self.read_from_url(decklist_url, "Downloading website:")
        with downloader, monitor:
            raw_data = downloader.read()
        encoding = re.search(
            r"charset=(?P<charset>[^;]+)", monitor.file.headers["Content-Type"]  # Match up to a potential ";"
        ).groupdict().get("charset", "utf-8")  # Fallback to utf-8, if the charset is not defined
        decoded_site = raw_data.decode(encoding)
        deck_id = re.search(r"/deck/download/(?P<deck_id>\d+)", decoded_site).group("deck_id")
        return deck_id


class MTGTop8Downloader(DecklistDownloader):
    """
    Downloader for https://mtgtop8.com. They host deck lists of tournaments
    """

    DECKLIST_PATH_RE = re.compile(
        r"https?://(www\.)?mtgtop8\.com/event\?e=\d+&d=(?P<deck_id>\d+).*?"
    )
    PARSER_CLASS = MagicWorkstationDeckDataFormatParser
    APPLICABLE_WEBSITES = "MTGTop8 (mtgtop8.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        deck_id = match["deck_id"]
        return f"http://mtgtop8.com/dec?d={deck_id}"


class MTGWTFDownloader(DecklistDownloader):
    """
    Downloader for https://mtg.wtf. They offer a list of all official pre-constructed decks in existence.
    """
    DECKLIST_PATH_RE = re.compile(
        r"https://mtg\.wtf/deck/\w+/(?P<name>\w+)/?"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "mtg.wtf"

    def post_process(self, data: bytes) -> str:
        deck_list = super().post_process(data)
        card_re = re.compile("(COMMANDER: )?(?P<content>[^/]+)")
        matches = map(card_re.match, deck_list.splitlines())
        lines = (match["content"] for match in matches if match is not None)
        return "\n".join(lines)

    def map_to_download_url(self, decklist_url: str) -> str:
        return f"{decklist_url}/download"


class TappedOutDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://tappedout\.net/mtg-decks/(?P<name>[-\w_%]+)/?"
    )
    PARSER_CLASS = TappedOutCSVParser
    APPLICABLE_WEBSITES = "TappedOut (tappedout.net)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        name = match.group("name")
        return f"https://tappedout.net/mtg-decks/{name}/?fmt=csv"


class MoxfieldDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?moxfield\.com/decks/(?P<moxfield_id>[-\w_]+)/?"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "Moxfield (moxfield.com)"

    @staticmethod
    def post_process(data: bytes) -> str:
        cards = []
        for board in (
                "mainboard", "sideboard", "commanders", "companions", "signatureSpells",
                "attractions", "stickers", "contraptions", "planes", "schemes"):
            cards += MoxfieldDownloader._read_board(data, f"boards.{board}.cards")
        buffer = StringIO(newline="")
        writer = csv.writer(buffer, MoxfieldDownloader.PARSER_CLASS.Dialect)
        writer.writerow(("count", "scryfall_id", "lang", "name", "set_code", "collector_number"))
        writer.writerows(cards)
        return buffer.getvalue()

    @staticmethod
    def _read_board(data: bytes, board: str) -> list[tuple[str, str, str, str, str, str]]:
        result = []
        for entry in next(ijson.items(data, board)).values():
            card = entry["card"]
            result.append(
                (str(entry["quantity"]), card["scryfall_id"], card["lang"], card["name"], card["set"], card["cn"]))
        return result

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        moxfield_id = match.group("moxfield_id")
        return f"https://api.moxfield.com/v3/decks/all/{moxfield_id}"


class DeckstatsDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://deckstats\.net/decks/(?P<user>\d+)/(?P<deck_id>\d+).*?"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "Deckstats (deckstats.net)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        user = match.group("user")
        deck_id = match.group("deck_id")
        # The deck is identified by a numerical deck id, followed by a hyphen and a deck name that can be anything.
        # It defaults to the set deck name, but everything after the hyphen is ignored by the server
        # The hyphen itself is required. Without it, the server returns the user's deck list directory.
        return f"https://deckstats.net/decks/{user}/{deck_id}-?" \
               f"include_comments=0&do_not_include_printings=0&export_mtgarena=1"


class ArchidektHTMLParser(html.parser.HTMLParser):

    def __init__(self, *, convert_charrefs: bool = True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.decklist_json = ""
        self.found_deck_tag = False

    def handle_starttag(self, tag: str, attrs: HTMLAttributeType) -> None:
        if tag == "script" and dict(attrs) == {"id": "__NEXT_DATA__", "type": "application/json"}:
            self.found_deck_tag = True

    def handle_data(self, data: str) -> None:
        if self.found_deck_tag:
            self.decklist_json = data
            self.found_deck_tag = False


class ArchidektDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?archidekt\.com/decks/(?P<deck_id>\d+).*?"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "Archidekt (archidekt.com)"

    def post_process(self, data: bytes) -> str:
        decoded = super().post_process(data)
        json_str = self._get_raw_deck_list_json(decoded)
        result = self._parse_json_deck_list(json_str)
        logger.debug(f"Obtained list list containing {len(result)-1} entries")
        return result

    @staticmethod
    def _get_raw_deck_list_json(data: str) -> str:
        parser = ArchidektHTMLParser()
        parser.feed(data)
        parser.close()
        return parser.decklist_json

    @staticmethod
    def _parse_json_deck_list(json_str: str) -> str:
        buffer = StringIO()
        writer = csv.writer(buffer, ScryfallCSVParser.Dialect)
        writer.writerow(["scryfall_id", "count", "lang", "name", "set_code", "collector_number"])
        encoded = json_str.encode("utf-8")
        # The cards are stored in a map, which looks like it uses some base64 keys of unknown origin/meaning
        # (e.g. "7ToxQpQbV") and card dicts as values.
        # We are interested in the map values, so access the map items via ijson.kvitems() and throw the keys away
        deck_items: JSONKeyValueType = ijson.kvitems(
            encoded, "props.pageProps.redux.deck.cardMap", use_float=True)
        writer.writerows(
            # The data does not contain a card language, so hard-code English
            (card["uid"], card["qty"], "en", card["name"], card["setCode"], card["collectorNumber"])
            for _, card in deck_items
        )
        return buffer.getvalue()


class MtgDecksNetDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://mtgdecks\.net/[A-Za-z]+/[-A-Za-z]+/?"
    )
    PARSER_CLASS = MTGArenaParser
    APPLICABLE_WEBSITES = "MTGDecks (mtgdecks.net)"

    def map_to_download_url(self, decklist_url: str) -> str:
        return f"{decklist_url}/txt"

    def post_process(self, data: bytes) -> str:
        deck_list = super().post_process(data)
        deck_list = deck_list.replace("/", " // ")
        return deck_list


class TCGPlayerDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://infinite\.tcgplayer\.com/magic-the-gathering/deck/[^/]+/(?P<deck_id>\d+).*?"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "TCGPlayer ∞ (infinite.tcgplayer.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        deck_id = match.group("deck_id")
        # cards enables inclusion of card data (in the form of a mapping from internal card id to card data),
        # subDecks enables inclusion of mainboard/sideboard as a tuple stream (internal card id, quantity)
        # stats enables irrelevant, additional card meta-data, like pricing and such, and is disabled.
        return f"https://infinite-api.tcgplayer.com/deck/magic/{deck_id}/?subDecks=true&cards=true&stats=false"

    def post_process(self, data: bytes) -> str:
        """
        TCGPlayer Infinite returns JSON with two relevant sections:
        Path result.deck.subDecks contains a mappings from (internal_card_id: card_copies) for each deck part
          (mainboard, sideboard, …).
        Path result.cards contains the de-duplicated list of all cards in the deck as JSON dicts. Entries contain
          an image URL containing the Scryfall-id, the internal_card_id also used in result.deck.subDecks
          and some other fields.
        """
        card_counts = self._gather_card_counts(data)
        buffer = StringIO()
        scryfall_id_re = re.compile(r"(?P<scryfall_id>[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12})")
        writer = csv.writer(buffer, ScryfallCSVParser.Dialect)
        writer.writerow(["scryfall_id", "count", "lang", "name", "set_code", "collector_number"])
        items: JSONKeyValueType = ijson.kvitems(data, "result.cards")
        # The data contains a URL to an image hosted on scryfall that contains the scryfall id
        # The data does not contain a card language, so hard-code English
        writer.writerows(
            (scryfall_id_re.search(card_data["scryfallImageURL"])["scryfall_id"], card_counts[card_id],
             "en", card_data["name"], card_data["set"].lower(), "")
            for card_id, card_data in items
        )
        return buffer.getvalue()

    @staticmethod
    def _gather_card_counts(data: bytes) -> Counter[str]:
        items: JSONKeyValueType = ijson.kvitems(data, "result.deck.subDecks")
        result = Counter()
        for _, counts in items:  # Ignore the board type "maindeck"/"sideboard"
            for card in counts:  # type: dict[str, int]
                # card IDs are supplied as integers, but used elsewhere as strings. So convert them to strings
                result[str(card["cardID"])] += card["quantity"]
        return result


class CubeCobraDownloader(DecklistDownloader):
    """
    The site allows supplying custom images for cards, which people use to upload full custom magic sets.
    This downloader does not support custom card images, so custom magic sets uploaded there are also not supported
    """
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?cubecobra\.com/cube/[a-z]+/(?P<cube_name>[0-9A-Za-z-_]+).*?"
    )
    PARSER_CLASS = XMageParser
    APPLICABLE_WEBSITES = "CubeCobra (cubecobra.com)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        cube_name = match.group("cube_name")
        return f"https://cubecobra.com/cube/download/xmage/{cube_name}"


class ManaboxDownloader(DecklistDownloader):
    DECKLIST_PATH_RE = re.compile(
        r"https://(www\.)?manabox\.app/decks/(?P<deck_id>[a-zA-Z0-9_-]{22})/?.*"
    )
    PARSER_CLASS = ScryfallCSVParser
    APPLICABLE_WEBSITES = "ManaBox (manabox.app)"

    def map_to_download_url(self, decklist_url: str) -> str:
        match = self.DECKLIST_PATH_RE.match(decklist_url)
        deck_id = match.group("deck_id")
        return f"https://cloud.manabox.app/decks/{deck_id}"

    def post_process(self, data: bytes) -> str:
        cards: Iterable[dict[str, Any]] = ijson.items(data, "cards.item")
        buffer = io.StringIO()
        writer = csv.writer(buffer, self.PARSER_CLASS.Dialect)
        writer.writerow(("scryfall_id", "count", "lang", "name", "set_code", "collector_number"))
        writer.writerows(
            (c["scryfallId"], c["quantity"], "", c["name"], c["setId"], "")
            for c in cards
        )
        return buffer.getvalue()


AVAILABLE_DOWNLOADERS: dict[str, Type[DecklistDownloader]] = {
    downloader.__name__: downloader for downloader in [
        ArchidektDownloader,
        CubeCobraDownloader,
        DeckstatsDownloader,
        ManaboxDownloader,
        MTGTop8Downloader,
        MoxfieldDownloader,
        MTGAZoneDownloader,
        MtgDecksNetDownloader,
        MTGGoldfishDownloader,
        MTGWTFDownloader,
        ScryfallDownloader,
        TappedOutDownloader,
        TCGPlayerDownloader,
    ]
}


def get_downloader_class(url: str):
    """
    For a given URL, returns the class of a downloader supporting it.
    Returns None for unsupported URLs.
    """
    for downloader in AVAILABLE_DOWNLOADERS.values():
        if downloader.DECKLIST_PATH_RE.match(url) is not None:
            return downloader
    return None
