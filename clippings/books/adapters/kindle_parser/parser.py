from __future__ import annotations

import itertools
import logging
from datetime import datetime
from typing import TypeAlias, TypedDict

from clippings.books.adapters.kindle_parser.language import (
    DatePart,
    LanguageSettings,
    presets,
)

logger = logging.getLogger(__name__)


class ClippingMetadata(TypedDict):
    type: str
    page: tuple[int, int]
    location: tuple[int, int]
    added_at: datetime


class RawClipping(ClippingMetadata):
    title: str
    metadata: str
    content: list[str]


class KindleClippingsParser:
    def __init__(self) -> None:
        self._clippings: list[RawClipping] = []
        self._in_clipping = True
        self._separator = "=========="
        self._fsm = KindleClippingsFSM()
        self._metadata_parser = KindleClippingMetadataParser(presets)

    def add_line(self, line: str) -> None:
        line = line.strip()
        if self._fsm.current_state == "title":
            self._clippings.append({})  # type: ignore[typeddict-item]
            self._in_clipping = True

        if self._fsm.current_state == "title" and line:
            self._clippings[-1]["title"] = line
            self._fsm.next_state()
        elif self._fsm.current_state == "metadata" and line:
            self._clippings[-1].update(self._metadata_parser.parse(line))
            self._fsm.next_state()
        elif self._fsm.current_state == "content":
            if line == self._separator:
                self._fsm.next_state()
                self._in_clipping = False
                return
            self._clippings[-1].setdefault("content", []).append(line)

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


class CantParseMetadataError(Exception):
    pass


Lang: TypeAlias = str
Marker: TypeAlias = str


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
        self._search_langs: set[str] = set()
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

    def parse(self, metadata: str) -> ClippingMetadata | Exception:
        self._search_langs = set(self._possible_languages)
        clipping_type = self._parse_clipping_type(metadata)
        if isinstance(clipping_type, Exception):
            return clipping_type
        page, loc = self._parse_page_and_loc(metadata)
        added_at = self._parse_date(metadata)
        return {
            "type": clipping_type,
            "page": page,
            "location": loc,
            "added_at": added_at,
        }

    def _parse_clipping_type(self, metadata: str) -> str | CantParseMetadataError:
        markers = [
            (self._highlight_markers, "highlight"),
            (self._note_markers, "note"),
            (self._bookmark_markers, "bookmark"),
        ]
        lower_metadata = metadata.lower()
        for markers_map, clipping_type in markers:
            for marker, langs in markers_map.items():
                cross_langs = self._search_langs.intersection(langs)
                if cross_langs and marker in lower_metadata:
                    self._search_langs = cross_langs
                    return clipping_type

        return CantParseMetadataError(f"Can't find clipping type: {metadata}")

    def _parse_page_and_loc(
        self, metadata: str
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        metadata = metadata.strip()[1:]
        search_langs = self._search_langs
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
                cross_langs = search_langs.intersection(langs)
                if cross_langs and name in metadata:
                    return cross_langs
            return set()

        parts = [parse_int_pairs(item) for item in cleaned.split(";")]

        if len(parts) == 1:
            if location_langs := find_location_langs():
                self._search_langs = location_langs
                return (-1, -1), parts[0]
            return parts[0], (-1, -1)

        return parts[0], parts[1]

    def _parse_date(self, metadata: str) -> datetime:
        _, date_meta = metadata.rsplit("|", 1)
        date_map = {}
        month_meta_parts = date_meta.lower().split()
        for month, values in self._month_names.items():
            if "month" in date_map:
                break
            for lang, value in values:
                if lang in self._search_langs and month in month_meta_parts:
                    date_map["month"] = value
                    self._search_langs = {
                        lang for lang, _ in values if lang in self._search_langs
                    }
                    break

        twelve_hour_marks = {
            val
            for lang, val in self._twelve_hour_marks.items()
            if lang in self._search_langs
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
        langs = list(self._search_langs)
        if len(langs) > 1:
            logger.warning("Multiple languages found, %s, using: %s", langs, langs[0])
        for date_format in self._date_formats[langs[0]]:
            if len(date_format) == len(numbers):
                parsed_date = dict(zip(date_format, numbers))
                for type, part_value in parsed_date.items():
                    if type == DatePart.YEAR:
                        date_map["year"] = int(part_value)
                    elif type == DatePart.MONTH:
                        date_map["month"] = int(part_value)
                    elif type == DatePart.MONTH_ISO:
                        date_map["month"] = int(part_value) + 1
                    elif type == DatePart.DAY:
                        date_map["day"] = int(part_value)
                    elif type == DatePart.TIME:
                        hour, minute, second = part_value.split(":")
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
        return result
