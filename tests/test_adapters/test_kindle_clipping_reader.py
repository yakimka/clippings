import io
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import pytest

from clippings.books.adapters.readers import KindleClippingsReader
from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import ClippingType


@pytest.fixture()
def make_sut():
    def _make_sut(file_object):
        return KindleClippingsReader(file_object)

    return _make_sut


@pytest.fixture()
def make_file_object():
    def _make_file_object(
        title: str = "Hexagonal Architecture Explained",
        author: str = "Cockburn, Alistair",
        metadata: str = (
            "- Your Highlight on page 112"
            " | location 1300-1301 | Added on Thursday, 22 August 2024 18:10:53"
        ),
        content: str = "My highlight",
    ) -> io.StringIO:
        clipping = [f"{title} ({author})", metadata, "", content, "=========="]
        return io.StringIO("\n".join(clipping))

    return _make_file_object


def make_metadata_string(
    location_part: str,
    # parser dont fail if date_part is empty
    #   so fo testing purposes we can pass empty string
    date_part: str = "",
) -> str:
    return f"{location_part} | {date_part}"


@pytest.fixture()
def multilanguage_clippings():
    this_dir = Path(__file__).parent
    with open(
        this_dir / "my_clippings_languages_examples.txt", encoding="utf-8-sig"
    ) as file:
        yield file


async def test_parse_book_title(make_file_object, make_sut):
    file = make_file_object(
        title="Hexagonal Architecture Explained",
        author="Cockburn, Alistair",
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    title = clippings[0].book_title
    assert title == "Hexagonal Architecture Explained (Cockburn, Alistair)"


@pytest.mark.parametrize(
    "metadata, expected_type",
    [
        pytest.param(
            make_metadata_string("- Your Highlight on page 1 | Location 1"),
            ClippingType.HIGHLIGHT,
            id="english highlight",
        ),
        pytest.param(
            make_metadata_string("- Your Note on page 1 | location 1"),
            ClippingType.NOTE,
            id="english note",
        ),
    ],
)
async def test_parse_clipping_type(
    metadata: str, expected_type: ClippingType, make_file_object, make_sut
):
    file = make_file_object(metadata=metadata)
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].type == expected_type


async def test_skip_bookmarks(make_file_object, make_sut):
    file = make_file_object(
        metadata=make_metadata_string("- Your Bookmark on page 112 | location 1300")
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert clippings == []


@pytest.mark.parametrize(
    "date_part",
    [
        "",
        "Added on Thursday",
        "Added on Thursday, 22 August 2024",
        # "Added on Thursday, 22 August 2024 18",
    ],
)
async def test_use_default_date_if_cant_parse(date_part, make_file_object, make_sut):
    file = make_file_object(
        metadata=make_metadata_string(
            date_part=date_part,
            location_part="- Your Highlight on page 1 | location 1",
        )
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].added_at == datetime(1970, 1, 1)


async def test_can_parse_single_valued_locations(make_file_object, make_sut):
    file = make_file_object(
        metadata=make_metadata_string("- Your Highlight on page 1 | location 2")
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].page == (1, 1)
    assert clippings[0].location == (2, 2)


@pytest.mark.parametrize(
    "metadata",
    [
        pytest.param(
            make_metadata_string("- Your Highlight on page 1-10 | location 2-20"),
            id="hyphen",
        ),
        pytest.param(
            make_metadata_string(
                "– Ваш выделенный отрывок на странице 1–10 | Место 2–20"
            ),
            id="dash",
        ),
        pytest.param(
            make_metadata_string(
                "- Je highlight op pagina 1 t/m 10 | locatie 2 t/m 20"
            ),
            id="dutch",
        ),
    ],
)
async def test_can_parse_ranged_locations(metadata: str, make_file_object, make_sut):
    file = make_file_object(metadata=metadata)
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].page == (1, 10)
    assert clippings[0].location == (2, 20)


async def test_can_parse_metadata_without_location(make_file_object, make_sut):
    file = make_file_object(
        metadata=make_metadata_string(
            "- Your Highlight on page 42", "Added on Thursday, 22 August 2024 18:10:53"
        )
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].page == (42, 42)
    assert clippings[0].location == (-1, -1)
    assert clippings[0].added_at == datetime(2024, 8, 22, 18, 10, 53)


async def test_can_parse_metadata_without_page(make_file_object, make_sut):
    file = make_file_object(
        metadata=make_metadata_string(
            "- Your Highlight at location 1430-1439",
            "Added on Thursday, 22 August 2024 18:10:53",
        )
    )
    sut = make_sut(file)
    clippings = [clipping async for clipping in sut.read()]

    assert len(clippings) == 1
    assert clippings[0].page == (-1, -1)
    assert clippings[0].location == (1430, 1439)
    assert clippings[0].added_at == datetime(2024, 8, 22, 18, 10, 53)


async def test_parsing_languages(make_sut, multilanguage_clippings):
    sut = make_sut(multilanguage_clippings)

    clippings = []
    async for clipping in sut.read():
        clippings.append(
            ClippingImportCandidateDTO(**(asdict(clipping) | {"content": "content"}))
        )

    assert len(clippings) == 22
    assert set(clippings) == {
        ClippingImportCandidateDTO(
            book_title="Hexagonal Architecture Explained (Cockburn, Alistair)",
            page=(112, 112),
            location=(1300, 1300),
            type=ClippingType.NOTE,
            content="content",
            added_at=datetime(2024, 8, 22, 18, 10, 53),
        ),
        ClippingImportCandidateDTO(
            book_title="Hexagonal Architecture Explained (Cockburn, Alistair)",
            page=(112, 112),
            location=(1300, 1301),
            type=ClippingType.HIGHLIGHT,
            content="content",
            added_at=datetime(2024, 8, 22, 18, 10, 53),
        ),
    }
