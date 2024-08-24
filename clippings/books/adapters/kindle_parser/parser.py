from __future__ import annotations

import itertools
import logging
from datetime import UTC, datetime
from typing import TypeAlias, TypedDict

from clippings.books.adapters.kindle_parser.language import (
    DatePart,
    LanguageSettings,
    presets,
)

logger = logging.getLogger(__name__)


Lang: TypeAlias = str
Marker: TypeAlias = str
Position: TypeAlias = tuple[int, int]


class ClippingMetadata(TypedDict):
    type: str
    page: Position
    location: Position
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

    def _parse_page_and_loc(self, metadata: str) -> tuple[Position, Position]:
        parser = PositionParser(
            metadata=metadata,
            search_langs=set(self._search_langs),
            range_delimiters=self._range_delimiters,
            page_and_loc_delimiters=self._page_and_loc_delimiters,
            page_markers=self._page_markers,
            location_markers=self._location_markers,
        )
        result = parser.parse()
        self._search_langs = set(parser.search_langs)
        return result

    def _parse_date(self, metadata: str) -> datetime:
        parser = DatetimeParser(
            metadata=metadata,
            search_langs=set(self._search_langs),
            month_names=self._month_names,
            twelve_hour_marks=self._twelve_hour_marks,
            date_formats=self._date_formats,
        )
        result = parser.parse()
        self._search_langs = set(parser.search_langs)
        return result


class PositionParser:
    def __init__(
        self,
        metadata: str,
        search_langs: set[str],
        range_delimiters: dict[Lang, str],
        page_and_loc_delimiters: dict[Lang, str],
        page_markers: dict[Marker, list[Lang]],
        location_markers: dict[Marker, list[Lang]],
    ) -> None:
        self._metadata = metadata
        self._cleaned = ""
        self.search_langs = search_langs
        self._range_delimiters_map = range_delimiters
        self._page_and_loc_delimiters_map = page_and_loc_delimiters
        self._page_markers = page_markers
        self._location_markers = location_markers

    @property
    def _range_delimiters(self) -> set[str]:
        return {
            val
            for lang, val in self._range_delimiters_map.items()
            if lang in self.search_langs
        }

    @property
    def _page_and_loc_delimiters(self) -> set[str]:
        return {
            val
            for lang, val in self._page_and_loc_delimiters_map.items()
            if lang in self.search_langs
        }

    def parse(self) -> tuple[Position, Position]:
        self._narrow_down_languages(self._page_markers)
        has_location = self._narrow_down_languages(self._location_markers)
        self._clean_metadata()
        page, loc = self._parse_positions(has_location)
        absent_value = (-1, -1)
        return page or absent_value, loc or absent_value

    def _clean_metadata(self) -> None:
        metadata = self._metadata.strip()[1:]
        range_delimiters = self._range_delimiters
        page_and_loc_delimiters = self._page_and_loc_delimiters
        replacers = [
            (" ", ""),
            *[(delim, "_") for delim in range_delimiters],
            *[(delim, ";") for delim in page_and_loc_delimiters],
        ]
        loc_meta, _ = metadata.rsplit("|", 1)
        for replacer in replacers:
            loc_meta = loc_meta.replace(*replacer)
        self._cleaned = "".join(char for char in loc_meta if char in "0123456789_;")

    def _parse_positions(
        self, has_location: bool
    ) -> tuple[Position | None, Position | None]:
        parts = [self._parse_int_pairs(item) for item in self._cleaned.split(";")]

        if len(parts) == 1:
            return (None, parts[0]) if has_location else (parts[0], None)
        return parts[0], parts[1]

    def _narrow_down_languages(self, markers: dict[Marker, list[Lang]]) -> bool:
        for name, langs in markers.items():
            cross_langs = self.search_langs.intersection(langs)
            if cross_langs and name in self._metadata:
                self.search_langs = cross_langs
                return True
        return False

    def _parse_int_pairs(self, text: str) -> Position:
        ints = text.split("_")
        if len(ints) == 1:
            return int(ints[0]), int(ints[0])
        return int(ints[0]), int(ints[1])


class DatetimeParser:
    def __init__(
        self,
        metadata: str,
        search_langs: set[str],
        month_names: dict[str, list[tuple[Lang, int]]],
        twelve_hour_marks: dict[Lang, tuple[str, str]],
        date_formats: dict[Lang, list[tuple[DatePart, ...]]],
    ):
        self._metadata = metadata
        self._cleaned = ""
        self.search_langs = search_langs
        self._month_names = month_names
        self._twelve_hour_marks_map = twelve_hour_marks
        self._date_formats = date_formats

    @property
    def _twelve_hour_marks(self) -> set[tuple[str, str]]:
        return {
            val
            for lang, val in self._twelve_hour_marks_map.items()
            if lang in self.search_langs
        }

    def parse(self) -> datetime:
        self._extract_date_part()
        month = self._search_month_in_text()
        self._clean_metadata()
        datetime_parts = self._parse_datetime_parts()
        if not datetime_parts:
            return datetime(1970, 1, 1)
        if "month" not in datetime_parts:
            datetime_parts["month"] = month
        return datetime(**datetime_parts)

    def _extract_date_part(self) -> None:
        self._metadata = self._metadata.rsplit("|", 1)[1]

    def _clean_metadata(self) -> None:
        numbers_parts = []
        twelve_hour_marks = self._twelve_hour_marks
        last_twelve_hour_chars = {
            item[-1] for item in twelve_hour_marks for item in item
        }
        for i, char in enumerate(self._metadata):
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
                        if self._metadata[: i + 1].endswith(mark)
                    ]
                    if len(found_marks) > 1:
                        raise RuntimeError("Multiple twelve hour marks found")
                    if found_marks:
                        numbers_parts.extend(found_marks)
                        numbers_parts.append(" ")
                elif prev_char != " ":
                    numbers_parts.append(" ")

        self._cleaned = "".join(numbers_parts).strip()

    def _search_month_in_text(self) -> int | None:
        month_meta_parts = self._metadata.lower().split()
        for month, values in self._month_names.items():
            for lang, value in values:
                if lang in self.search_langs and month in month_meta_parts:
                    self.search_langs = {
                        lang for lang, _ in values if lang in self.search_langs
                    }
                    return value
        return None

    def _parse_datetime_parts(self) -> dict[str, int]:
        numbers = self._cleaned.split(" ")
        langs = list(self.search_langs)
        if len(langs) > 1:
            logger.warning("Multiple languages found, %s, using: %s", langs, langs[0])
        for date_format in self._date_formats[langs[0]]:
            result: dict[str, int] = {}
            if len(date_format) != len(numbers):
                continue
            parsed_date = dict(zip(date_format, numbers))
            for type, part_value in parsed_date.items():
                if type == DatePart.YEAR:
                    result["year"] = int(part_value)
                elif type == DatePart.MONTH:
                    result["month"] = int(part_value)
                elif type == DatePart.MONTH_ISO:
                    result["month"] = int(part_value) + 1
                elif type == DatePart.DAY:
                    result["day"] = int(part_value)
                elif type == DatePart.TIME:
                    hour, minute, second = part_value.split(":")
                    if mark := parsed_date.get(DatePart.TWElVE_HOUR_MARK):
                        if hour == "12" and mark == "AM":
                            hour = 0
                        elif mark == "PM":
                            hour = int(hour) + 12
                    result["hour"] = int(hour)
                    result["minute"] = int(minute)
                    result["second"] = int(second)
            # TODO check result for validity
            if result:
                return result
        return {}
