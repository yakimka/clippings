from pathlib import Path

import pytest

from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def client_auth():
    return ("testuser", "testpass")


@pytest.fixture()
def clippings_for_upload():
    this_dir = Path(__file__).parent
    fixture = this_dir / "clippings_for_upload.txt"
    with open(fixture, "rb") as file:
        yield file


@pytest.fixture()
def data_for_restore():
    this_dir = Path(__file__).parent
    fixture = this_dir / "my-clippings-backup.ndjson"
    with open(fixture, "rb") as file:
        yield file


async def test_home_page(client):
    response = await client.get("/", follow_redirects=True)

    assert response.status_code == 200


@pytest.mark.parametrize(
    "url_template",
    [
        item.template
        for item in urls_manager
        if item.method == "get" and item.id not in ("home_page", "logout")
    ],
)
async def test_get_endpoints(client, book_storage, mother, url_template):
    inline_note = mother.inline_note(id="inlinenote1")
    clipping = mother.clipping(id="clipping1", inline_notes=[inline_note])
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = url_template.format(
        book_id="book1", clipping_id="clipping1", inline_note_id="inlinenote1"
    )

    response = await client.get(url)

    assert response.status_code == 200, url


@pytest.mark.parametrize(
    "url_template",
    [
        item.template
        for item in urls_manager.get_by_tag("book")
        if item.method == "delete"
    ],
)
async def test_books_delete_endpoints(client, book_storage, mother, url_template):
    inline_note = mother.inline_note(id="inlinenote1")
    clipping = mother.clipping(id="clipping1", inline_notes=[inline_note])
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = url_template.format(
        book_id="book1", clipping_id="clipping1", inline_note_id="inlinenote1"
    )

    response = await client.delete(url)

    assert response.status_code in (200, 303)


async def test_import_clippings(client, book_storage, clippings_for_upload):
    url = urls_manager.build_url("clipping_upload").value
    response = await client.post(url, files={"file": clippings_for_upload})

    assert response.status_code == 200
    books = await book_storage.find()
    assert len(books) == 1


async def test_restore_data(client, book_storage, data_for_restore):
    url = urls_manager.build_url("clippings_restore").value
    response = await client.post(url, files={"file": data_for_restore})

    assert response.status_code == 200
    books = await book_storage.find()
    assert len(books) > 1


async def test_update_book_info(client, book_storage, mother):
    book = mother.book(id="book1")
    await book_storage.add(book)
    url = urls_manager.build_url("book_info_update", book_id="book1").value
    response = await client.put(
        url,
        data={
            "title": "new title",
            "authors": "new author1 & new author2",
            "rating": "5",
        },
    )

    assert response.status_code == 303
    updated_book = await book_storage.get("book1")
    assert updated_book.title == "new title"
    assert updated_book.authors == ["new author1", "new author2"]
    assert updated_book.rating == 5


async def test_update_book_review(client, book_storage, mother):
    book = mother.book(id="book1")
    await book_storage.add(book)
    url = urls_manager.build_url("book_review_update", book_id="book1").value
    response = await client.put(url, data={"review": "new review"})

    assert response.status_code == 303
    assert (await book_storage.get("book1")).review == "new review"


async def test_update_clipping(client, book_storage, mother):
    clipping = mother.clipping(id="clipping1")
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = urls_manager.build_url(
        "clipping_update", book_id="book1", clipping_id="clipping1"
    ).value
    response = await client.put(url, data={"content": "new content"})

    assert response.status_code == 303
    updated_clipping = (await book_storage.get("book1")).get_clipping("clipping1")
    assert updated_clipping.content == "new content"


async def test_add_inline_note(client, book_storage, mother):
    clipping = mother.clipping(id="clipping1")
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = urls_manager.build_url(
        "inline_note_add", book_id="book1", clipping_id="clipping1"
    ).value
    response = await client.post(url, data={"content": "new note"})

    assert response.status_code == 303
    updated_clipping = (await book_storage.get("book1")).get_clipping("clipping1")
    assert updated_clipping.inline_notes[0].content == "new note"


async def test_unlink_inline_note(client, book_storage, mother):
    inline_note = mother.inline_note(id="inlinenote1", automatically_linked=True)
    clipping = mother.clipping(id="clipping1", inline_notes=[inline_note])
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = urls_manager.build_url(
        "inline_note_unlink",
        book_id="book1",
        clipping_id="clipping1",
        inline_note_id="inlinenote1",
    ).value
    response = await client.post(url)

    assert response.status_code == 303
    updated_clipping = (await book_storage.get("book1")).get_clipping("clipping1")
    assert not updated_clipping.inline_notes


async def test_update_inline_note(client, book_storage, mother):
    inline_note = mother.inline_note(id="inlinenote1")
    clipping = mother.clipping(id="clipping1", inline_notes=[inline_note])
    book = mother.book(id="book1", clippings=[clipping])
    await book_storage.add(book)
    url = urls_manager.build_url(
        "inline_note_update",
        book_id="book1",
        clipping_id="clipping1",
        inline_note_id="inlinenote1",
    ).value
    response = await client.put(url, data={"content": "new content"})

    assert response.status_code == 303
    updated_clipping = (await book_storage.get("book1")).get_clipping("clipping1")
    assert updated_clipping.inline_notes[0].content == "new content"


async def test_clear_deleted_hashes(client):
    url = urls_manager.build_url("deleted_hash_clear").value
    response = await client.post(url)

    assert response.status_code == 200
