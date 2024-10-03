import pytest

from clippings.books.dtos import BookInfoSearchResultDTO
from clippings.books.use_cases.book_info import GoogleBookInfoClient

pytestmark = pytest.mark.vcr(filter_query_parameters=["key"])


@pytest.fixture()
async def make_sut():
    client: GoogleBookInfoClient | None = None

    def _make_sut():
        nonlocal client
        client = GoogleBookInfoClient(timeout=1, api_key=None)
        return client  # noqa: PIE781

    yield _make_sut
    if client is not None:
        await client.aclose()


async def test_find_book_by_title(make_sut):
    sut = make_sut()

    result = await sut.get("The Hitchhiker's Guide to the Galaxy", "Douglas Adams")

    img_url = "http://books.google.com/books/content"
    assert result == BookInfoSearchResultDTO(
        isbns=["9780330513081", "0330513087"],
        title="The Hitchhiker's Guide to the Galaxy",
        authors=["Douglas Adams"],
        cover_image_small=f"{img_url}?id=DmUr6q1EDYMC&printsec=frontcover&img=1&zoom=1",
        cover_image_big=f"{img_url}?id=DmUr6q1EDYMC&printsec=frontcover&img=1&zoom=3",
    )


async def test_author_is_used_if_present(make_sut):
    sut = make_sut()

    result = await sut.get("The Hitchhiker's Guide to the Galaxy", "Stephen King")

    assert result.authors == ["Stephen King"]


async def test_return_none_if_cant_find_book(make_sut):
    sut = make_sut()

    result = await sut.get("something with ч", "Abracadabra")

    assert result is None
