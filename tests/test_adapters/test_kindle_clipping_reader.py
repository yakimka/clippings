from datetime import datetime

import pytest

from clippings.books.adapters.readers import (
    KindleClippingMetadata,
    KindleClippingMetadataParser,
    KindleClippingsReader,
    language_settings,
)


@pytest.fixture()
def make_sut():
    def _make_sut(file_object):
        return KindleClippingsReader(file_object)

    return _make_sut


@pytest.fixture()
def multilanguage_clippings():
    with open("my_clippings_languages_examples.txt") as file:
        yield file


async def test_parsing_languages(make_sut, multilanguage_clippings):
    parser = KindleClippingMetadataParser(language_settings)
    sut = make_sut(multilanguage_clippings)
    clippings = [clipping async for clipping in sut.read()]

    result = [parser.parse(item["metadata"]) for item in clippings]

    assert set(result) == {
        KindleClippingMetadata(
            type="highlight",
            page=(112, 112),
            location=(1300, 1301),
            added_at=datetime(2024, 8, 22, 18, 10, 53),
        ),
        KindleClippingMetadata(
            type="note",
            page=(112, 112),
            location=(1300, 1300),
            added_at=datetime(2024, 8, 22, 18, 10, 53),
        ),
        KindleClippingMetadata(
            type="bookmark",
            page=(112, 112),
            location=(1300, 1300),
            added_at=datetime(2024, 8, 22, 18, 10, 53),
        ),
    }
