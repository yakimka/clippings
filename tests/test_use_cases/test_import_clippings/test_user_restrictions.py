from __future__ import annotations

import pytest

from clippings.books.adapters import id_generators
from clippings.books.use_cases.import_clippings import ImportClippingsUseCase
from clippings.seedwork.exceptions import QuotaExceededError

pytestmark = pytest.mark.usefixtures("user")


@pytest.fixture()
def sut(
    mock_book_storage,
    mock_clipping_reader,
    mock_deleted_hash_storage,
    enrich_books_meta_service,
    mock_users_storage,
) -> ImportClippingsUseCase:
    return ImportClippingsUseCase(
        storage=mock_book_storage,
        reader=mock_clipping_reader,
        deleted_hash_storage=mock_deleted_hash_storage,
        enrich_books_meta_service=enrich_books_meta_service,
        book_id_generator=lambda book: book.title,
        clipping_id_generator=id_generators.clipping_id_generator,
        inline_note_id_generator=id_generators.inline_note_id_generator,
        users_storage=mock_users_storage,
    )


async def test_cant_import_more_books_than_limit_when_user_has_0_books(
    sut, mother, mock_clipping_reader, mock_users_storage
):
    await mock_users_storage.add(
        mother.user(
            id="user_id_1",
            max_books=3,
        )
    )
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title=f"The Book {i}",
        )
        for i in range(4)
    ]

    with pytest.raises(QuotaExceededError) as exc:
        await sut.execute(user_id="user_id_1")

    assert exc.value.quota_type == "books"
    assert exc.value.current_quota == 3
    assert exc.value.trying_to_add == 4


async def test_cant_import_more_books_than_limit_when_user_already_has_books(
    sut, mother, mock_clipping_reader, mock_book_storage, mock_users_storage
):
    await mock_users_storage.add(
        mother.user(
            id="user_id_1",
            max_books=3,
        )
    )
    await mock_book_storage.extend(
        [
            mother.book(
                id=f"book_id_{i}",
                title=f"The Book {i}",
            )
            for i in range(3)
        ]
    )
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="New Book",
        )
    ]

    with pytest.raises(QuotaExceededError) as exc:
        await sut.execute(user_id="user_id_1")

    assert exc.value.quota_type == "books"
    assert exc.value.current_quota == 3
    assert exc.value.trying_to_add == 1


async def test_cant_import_more_clippings_than_limit_when_user_has_0_books(
    sut, mother, mock_clipping_reader, mock_users_storage
):
    await mock_users_storage.add(
        mother.user(
            id="user_id_1",
            max_clippings_per_book=3,
        )
    )
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            page=(1, 1),
        )
        for i in range(4)
    ]

    with pytest.raises(QuotaExceededError) as exc:
        await sut.execute(user_id="user_id_1")

    assert exc.value.quota_type == "clippings"
    assert exc.value.current_quota == 3
    assert exc.value.trying_to_add == 4


async def test_cant_import_more_clippings_than_limit_when_user_already_has_clippings(
    sut, mother, mock_clipping_reader, mock_book_storage, mock_users_storage
):
    await mock_users_storage.add(
        mother.user(
            id="user_id_1",
            max_clippings_per_book=3,
        )
    )
    await mock_book_storage.extend(
        [
            mother.book(
                id="The Book",
                title="The Book",
                clippings=[
                    mother.clipping(
                        id="clipping_id_1",
                        page=(1, 1),
                    ),
                    mother.clipping(
                        id="clipping_id_2",
                        page=(2, 2),
                    ),
                    mother.clipping(
                        id="clipping_id_3",
                        page=(3, 3),
                    ),
                ],
            )
        ]
    )
    mock_clipping_reader.clippings = [
        mother.clipping_import_candidate_dto(
            book_title="The Book",
            page=(12, 1),
        )
    ]

    with pytest.raises(QuotaExceededError) as exc:
        await sut.execute(user_id="user_id_1")

    assert exc.value.quota_type == "clippings"
    assert exc.value.current_quota == 3
    assert exc.value.trying_to_add == 1
