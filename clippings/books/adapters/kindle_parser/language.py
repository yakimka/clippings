from __future__ import annotations

from builtins import ValueError
from dataclasses import dataclass
from enum import Enum, auto


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

    def __post_init__(self):
        if self.month_names and len(self.month_names) != 12:
            raise ValueError(
                f"{self.language_name}: `month_names` must be length of 12"
            )
        required = [
            "language_name",
            "highlight_marker",
            "note_marker",
            "bookmark_marker",
            "page_marker",
            "location_marker",
            "range_delimiter",
            "page_and_location_delimiter",
        ]
        for field_name in required:
            if not getattr(self, field_name):
                raise ValueError(f"{self.language_name}: `field_name` is required")


presets = [
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
