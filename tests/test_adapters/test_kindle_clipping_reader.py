from dataclasses import asdict
from datetime import datetime

import pytest

from clippings.books.adapters.readers import (
    KindleClippingMetadataParser,
    KindleClippingsReader,
    language_settings,
)
from clippings.books.dtos import ClippingImportCandidateDTO
from clippings.books.entities import ClippingType


@pytest.fixture()
def make_sut():
    def _make_sut(file_object):
        return KindleClippingsReader(file_object)

    return _make_sut


@pytest.fixture()
def multilanguage_clippings():
    with open("my_clippings_languages_examples.txt", encoding="utf-8-sig") as file:
        yield file


async def test_parsing_languages(make_sut, multilanguage_clippings):
    sut = make_sut(multilanguage_clippings)
    clippings = set()
    async for clipping in sut.read():
        clippings.add(
            ClippingImportCandidateDTO(**(asdict(clipping) | {"content": "content"}))
        )

    assert clippings == {
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
