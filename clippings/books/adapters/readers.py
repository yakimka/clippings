from __future__ import annotations

import io
import itertools
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, TypedDict

from clippings.books.ports import ClippingsReaderABC

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clippings.books.dtos import ClippingImportCandidateDTO


logger = logging.getLogger(__name__)


class MockClippingsReader(ClippingsReaderABC):
    def __init__(self, clippings: list[ClippingImportCandidateDTO]) -> None:
        self.clippings = clippings

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        for clipping in self.clippings:
            yield clipping


class KindleClippingsReader(ClippingsReaderABC):
    def __init__(self, file_object: io.TextIOWrapper) -> None:
        self._file_object = file_object

    async def read(self) -> AsyncGenerator[ClippingImportCandidateDTO, None]:
        parser = KindleClippingsParser()
        for line in self._file_object:
            parser.add_line(line)
            if clipping := parser.get_clipping():
                yield clipping


class DatePart(Enum):
    YEAR = auto()
    MONTH = auto()
    MONTH_ISO = auto()
    DAY = auto()
    TIME = auto()
    TWElVE_HOUR_MARK = auto()
    SKIP = auto()


@dataclass(kw_only=True)
class LanguageSettings:
    language_name: str
    highlight_marker: str
    note_marker: str
    bookmark_marker: str
    page_marker: str
    location_marker: str
    range_delimiter: str
    page_and_location_delimiter: str
    month_names: list[str]
    date_formats: list[tuple[DatePart, ...]]
    twelve_hour_mark: tuple[str, str] | None = None


language_settings = [
    LanguageSettings(
        language_name="English",
        highlight_marker="highlight",
        note_marker="note",
        bookmark_marker="bookmark",
        page_marker="page",
        location_marker="location",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ],
        twelve_hour_mark=("AM", "PM"),
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME, DatePart.TWElVE_HOUR_MARK),
        ],
    ),
    LanguageSettings(
        language_name="Português",
        highlight_marker="destaque",
        note_marker="nota",
        bookmark_marker="marcador",
        page_marker="página",
        location_marker="posição",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "janeiro",
            "fevereiro",
            "março",
            "abril",
            "maio",
            "junho",
            "julho",
            "agosto",
            "setembro",
            "outubro",
            "novembro",
            "dezembro",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Italiano",
        highlight_marker="evidenziazione",
        note_marker="nota",
        bookmark_marker="segnalibro",
        page_marker="pagina",
        location_marker="posizione",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "gennaio",
            "febbraio",
            "marzo",
            "aprile",
            "maggio",
            "giugno",
            "luglio",
            "agosto",
            "settembre",
            "ottobre",
            "novembre",
            "dicembre",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Nederlands",
        highlight_marker="highlight",
        note_marker="notitie",
        bookmark_marker="bladwijzer",
        page_marker="pagina",
        location_marker="locatie",
        range_delimiter="t/m",
        page_and_location_delimiter="|",
        month_names=[
            "januari",
            "februari",
            "maart",
            "april",
            "mei",
            "juni",
            "juli",
            "augustus",
            "september",
            "oktober",
            "november",
            "december",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Deutsch",
        highlight_marker="markierung",
        note_marker="notiz",
        bookmark_marker="lesezeichen",
        page_marker="seite",
        location_marker="position",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "januar",
            "februar",
            "märz",
            "april",
            "mai",
            "juni",
            "juli",
            "august",
            "september",
            "oktober",
            "november",
            "dezember",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Español",
        highlight_marker="subrayado",
        note_marker="nota",
        bookmark_marker="marcador",
        page_marker="página",
        location_marker="posición",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Français",
        highlight_marker="surlignement",
        note_marker="note",
        bookmark_marker="signet",
        page_marker="page",
        location_marker="emplacement",
        range_delimiter="-",
        page_and_location_delimiter="|",
        month_names=[
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Russian",
        highlight_marker="отрывок",
        note_marker="заметка",
        bookmark_marker="закладка",
        page_marker="страниц",
        location_marker="место",
        range_delimiter="–",
        page_and_location_delimiter="|",
        month_names=[
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря",
        ],
        date_formats=[
            (DatePart.DAY, DatePart.YEAR, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Japanese",
        highlight_marker="ハイライト",
        note_marker="のメモ",
        bookmark_marker="のブックマーク",
        page_marker="ページ",
        range_delimiter="-",
        page_and_location_delimiter="|",
        location_marker="位置",
        month_names=[],
        date_formats=[
            (DatePart.YEAR, DatePart.MONTH, DatePart.DAY, DatePart.TIME),
        ],
    ),
    LanguageSettings(
        language_name="Chinese",
        highlight_marker="的标",
        note_marker="的笔记",
        bookmark_marker="书签",
        page_marker="页",
        range_delimiter="-",
        page_and_location_delimiter="（",
        location_marker="位置",
        month_names=[],
        twelve_hour_mark=("上午", "下午"),
        date_formats=[
            (
                DatePart.YEAR,
                DatePart.MONTH,
                DatePart.DAY,
                DatePart.TWElVE_HOUR_MARK,
                DatePart.TIME,
            ),
        ],
    ),
]


class CantParseMetadataError(Exception):
    pass


type Lang = str
type Marker = str


class KindleClippingMetadataParser:
    def __init__(self, language_settings: list[LanguageSettings]) -> None:
        self._language_settings = language_settings
        self._highlight_markers: dict[Marker, list[Lang]] = {}
        self._note_markers: dict[Marker, list[Lang]] = {}
        self._bookmark_markers: dict[Marker, list[Lang]] = {}
        self._page_markers: dict[Marker, list[Lang]] = {}
        self._location_markers: dict[Marker, list[Lang]] = {}
        self._month_names: dict[str, list[tuple[Lang, int]]] = {}
        self._possible_languages: frozenset[str] = frozenset()
        self._range_delimiters: dict[Lang, str] = {}
        self._page_and_loc_delimiters: dict[Lang, str] = {}
        self._twelve_hour_marks: dict[Lang, tuple[str, str]] = {}
        self._date_formats: dict[Lang, list[tuple[DatePart, ...]]] = {}
        self.init_markers()

    def init_markers(self) -> None:
        possible_langs = set()
        for s in self._language_settings:
            lang = s.language_name
            possible_langs.add(lang)
            self._highlight_markers.setdefault(s.highlight_marker, []).append(lang)
            self._note_markers.setdefault(s.note_marker, []).append(lang)
            self._bookmark_markers.setdefault(s.bookmark_marker, []).append(lang)
            self._page_markers.setdefault(s.page_marker, []).append(lang)
            self._location_markers.setdefault(s.location_marker, []).append(lang)
            for i, month in enumerate(s.month_names, start=1):
                self._month_names.setdefault(month, []).append((lang, i))
            self._range_delimiters[lang] = s.range_delimiter
            self._page_and_loc_delimiters[lang] = s.page_and_location_delimiter
            if s.twelve_hour_mark:
                self._twelve_hour_marks[lang] = s.twelve_hour_mark
            self._date_formats[lang] = s.date_formats

        self._possible_languages = frozenset(possible_langs)

    def parse(self, metadata: str) -> KindleClippingMetadata | Exception:
        search_langs = set(self._possible_languages)
        clipping_res = self._parse_clipping_type(metadata, search_langs)
        if isinstance(clipping_res, Exception):
            return clipping_res
        clipping_type, search_langs = clipping_res
        page, loc, search_langs = self._parse_page_and_loc(metadata, search_langs)
        datetime, search_langs = self._parse_date(metadata, search_langs)
        return KindleClippingMetadata(
            type=clipping_type,
            page=page,
            location=loc,
            added_at=datetime,
        )

    def _parse_clipping_type(
        self, metadata: str, search_langs: set[str]
    ) -> tuple[str, set[str]] | CantParseMetadataError:
        original_metadata = metadata
        metadata = metadata.lower()
        for marker, langs in self._highlight_markers.items():
            if (cross_langs := search_langs.intersection(langs)) and marker in metadata:
                return "highlight", cross_langs
        for marker, langs in self._note_markers.items():
            if (cross_langs := search_langs.intersection(langs)) and marker in metadata:
                return "note", cross_langs
        for marker, langs in self._bookmark_markers.items():
            if (cross_langs := search_langs.intersection(langs)) and marker in metadata:
                return "bookmark", cross_langs

        return CantParseMetadataError(f"Can't find clipping type: {original_metadata}")

    def _parse_page_and_loc(
        self, metadata: str, search_langs: set[str]
    ) -> tuple[tuple[int, int], tuple[int, int], set[str]]:
        metadata = metadata.strip()[1:]
        range_delimiters = {
            val for lang, val in self._range_delimiters.items() if lang in search_langs
        }
        page_and_loc_delimiters = {
            val
            for lang, val in self._page_and_loc_delimiters.items()
            if lang in search_langs
        }
        replacers = [
            (" ", ""),
            *[(delim, "_") for delim in range_delimiters],
            *[(delim, ";") for delim in page_and_loc_delimiters],
        ]
        loc_meta, _ = metadata.rsplit("|", 1)
        for replacer in replacers:
            loc_meta = loc_meta.replace(*replacer)
        cleaned = "".join(char for char in loc_meta if char in "0123456789_;")

        def parse_int_pairs(text: str) -> tuple[int, int]:
            ints = text.split("_")
            if len(ints) == 1:
                return int(ints[0]), int(ints[0])
            return int(ints[0]), int(ints[1])

        def find_location_langs() -> set[str]:
            for name, langs in self._location_markers.items():
                if cross_langs := search_langs.intersection(langs):
                    if name in metadata:
                        return cross_langs
            return set()

        parts = [parse_int_pairs(item) for item in cleaned.split(";")]

        if len(parts) == 1:
            if location_langs := find_location_langs():
                return (-1, -1), parts[0], location_langs
            return parts[0], (-1, -1), search_langs

        return parts[0], parts[1], search_langs

    def _parse_date(
        self, metadata: str, search_langs: set[str]
    ) -> tuple[datetime, set[str]]:
        _, date_meta = metadata.rsplit("|", 1)
        date_map = {}
        month_meta_parts = date_meta.lower().split()
        for month, values in self._month_names.items():
            if "month" in date_map:
                break
            for lang, value in values:
                if lang in search_langs and month in month_meta_parts:
                    date_map["month"] = value
                    search_langs = {lang for lang, _ in values if lang in search_langs}
                    break

        twelve_hour_marks = {
            val for lang, val in self._twelve_hour_marks.items() if lang in search_langs
        }
        numbers_parts = []
        last_twelve_hour_chars = {
            item[-1] for item in twelve_hour_marks for item in item
        }
        for i, char in enumerate(date_meta):
            if char.isdigit():
                numbers_parts.append(char)
            elif numbers_parts:
                prev_char = numbers_parts[-1]
                if char == ":" and prev_char.isdigit():
                    numbers_parts.append(char)
                elif char in last_twelve_hour_chars:
                    found_marks = [
                        "AM" if mark_i == 0 else "PM"
                        for marks in twelve_hour_marks
                        for mark_i, mark in enumerate(marks)
                        if date_meta[: i + 1].endswith(mark)
                    ]
                    if len(found_marks) > 1:
                        raise RuntimeError("Multiple twelve hour marks found")
                    if found_marks:
                        numbers_parts.extend(found_marks)
                        numbers_parts.append(" ")
                elif prev_char != " ":
                    numbers_parts.append(" ")

        numbers = "".join(numbers_parts).strip().split(" ")
        langs = list(search_langs)
        if len(langs) > 1:
            logger.warning("Multiple languages found, %s, using: %s", langs, langs[0])
        for date_format in self._date_formats[langs[0]]:
            if len(date_format) == len(numbers):
                parsed_date = dict(zip(date_format, numbers))
                for type, value in parsed_date.items():
                    if type == DatePart.YEAR:
                        date_map["year"] = int(value)
                    elif type == DatePart.MONTH:
                        date_map["month"] = int(value)
                    elif type == DatePart.MONTH_ISO:
                        date_map["month"] = int(value) + 1
                    elif type == DatePart.DAY:
                        date_map["day"] = int(value)
                    elif type == DatePart.TIME:
                        hour, minute, second = value.split(":")
                        if mark := parsed_date.get(DatePart.TWElVE_HOUR_MARK):
                            if hour == "12" and mark == "AM":
                                hour = 0
                            elif mark == "PM":
                                hour = int(hour) + 12
                        date_map["hour"] = int(hour)
                        date_map["minute"] = int(minute)
                        date_map["second"] = int(second)

        try:
            result = datetime(**date_map)
        except (ValueError, TypeError):
            logger.exception("Can't parse date from metadata: %s", metadata)
            result = datetime(1970, 1, 1)
        return result, search_langs


@dataclass(kw_only=True, frozen=True)
class KindleClippingMetadata:
    type: str
    page: tuple[int, int]
    location: tuple[int, int]
    added_at: datetime


class RawClipping(TypedDict):
    title: str
    metadata: str
    content: list[str]


class KindleClippingsParser:
    def __init__(self) -> None:
        self._clippings: list[RawClipping] = []
        self._in_clipping = True
        self._separator = "=========="
        self._fsm = KindleClippingsFSM()

    def add_line(self, line: str) -> None:
        line = line.strip()
        if self._fsm.current_state == "title":
            self._clippings.append({})  # type: ignore[typeddict-item]
            self._in_clipping = True

        if self._fsm.current_state == "title" and line:
            self._clippings[-1]["title"] = line
            self._fsm.next_state()
            return
        if self._fsm.current_state == "metadata" and line:
            self._clippings[-1]["metadata"] = line
            self._fsm.next_state()
            return
        if self._fsm.current_state == "content":
            if line == self._separator:
                self._fsm.next_state()
                self._in_clipping = False
                return
            self._clippings[-1].setdefault("content", []).append(line)
            return

    def get_clipping(self) -> RawClipping | None:
        if self._in_clipping:
            return None
        try:
            return self._clippings.pop()
        except IndexError:
            return None


class KindleClippingsFSM:
    def __init__(self) -> None:
        self._states = itertools.cycle(
            [
                "title",
                "metadata",
                "content",
            ]
        )
        self.current_state = ""
        self.next_state()

    def next_state(self) -> None:
        self.current_state = next(self._states)
