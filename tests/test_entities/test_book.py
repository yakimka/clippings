import pytest

from clippings.books.adapters.id_generators import inline_note_id_generator
from clippings.books.entities import ClippingType
from clippings.seedwork.exceptions import DomainError


class TestAuthorsSerialization:
    def test_to_string(self, mother):
        book = mother.book(authors=["Author 1", "Author 2"])

        result = book.authors_to_str()

        assert result == "Author 1 & Author 2"

    def test_set_from_string(self, mother):
        book = mother.book()

        book.authors_from_str("Author 1 & Author 2")

        assert book.authors == ["Author 1", "Author 2"]


class TestAddClippings:
    def test_add_clippings(self, mother):
        book = mother.book()
        clippings = [
            mother.clipping(id="1"),
            mother.clipping(id="2"),
            mother.clipping(id="3"),
        ]

        added_count = book.add_clippings(clippings)

        assert added_count == 3
        assert book.clippings == clippings

    def test_dont_add_clippings_if_already_exist(self, mother):
        book = mother.book()
        clippings = [
            mother.clipping(id="1"),
            mother.clipping(id="2"),
            mother.clipping(id="3"),
        ]
        book.add_clippings(clippings)

        added_count = book.add_clippings(clippings)

        assert added_count == 0
        assert book.clippings == clippings

    def test_dont_add_clipping_if_it_linked_as_inline_note(self, mother):
        book = mother.book()
        clippings = [
            mother.clipping(id="1", inline_notes=[mother.inline_note(original_id="2")]),
            mother.clipping(id="3"),
        ]
        book.add_clippings(clippings)

        added_count = book.add_clippings([mother.clipping(id="2")])

        assert added_count == 0
        assert book.clippings == clippings


@pytest.mark.parametrize(
    "highlight_page,highlight_loc,note_page,note_loc",
    [
        pytest.param((10, 10), (-1, -1), (10, 10), (-1, -1), id="link by page"),
        pytest.param((10, 20), (-1, -1), (10, 10), (-1, -1), id="link by start page"),
        pytest.param(
            (10, 10),
            (-1, -1),
            (10, 20),
            (-1, -1),
            id="link by start page even if note end page is after highlight",
        ),
        pytest.param((-1, -1), (42, 42), (-1, -1), (42, 42), id="link by location"),
        pytest.param(
            (-1, -1), (42, 142), (-1, -1), (42, 42), id="link by start location"
        ),
        pytest.param(
            (-1, -1),
            (42, 142),
            (-1, -1),
            (42, 242),
            id="link by start locationeven if note end page is after highlight",
        ),
    ],
)
@pytest.mark.parametrize("clippings_order_desc", [False, True])
def test_link_note_that_has_position_relevant_to_highlight(
    highlight_page,
    highlight_loc,
    note_page,
    note_loc,
    clippings_order_desc,
    mother,
):
    book = mother.book()
    clippings = sorted(
        [
            mother.clipping(
                id="1",
                page=highlight_page,
                location=highlight_loc,
                type=ClippingType.HIGHLIGHT,
            ),
            mother.clipping(
                id="2", page=note_page, location=note_loc, type=ClippingType.NOTE
            ),
        ],
        key=lambda x: x.id,
        reverse=clippings_order_desc,
    )
    book.add_clippings(clippings)

    book.link_notes(inline_note_id_generator=inline_note_id_generator)

    assert len(book.clippings) == 1
    clipping = book.clippings[0]
    assert clipping.id == "1"
    assert len(clipping.inline_notes) == 1
    assert clipping.inline_notes[0].original_id == "2"
    assert clipping.inline_notes[0].id != "2"


class TestUnlinkInlineNote:
    def test_return_error_if_cant_find_clipping(self, mother):
        inline_note = mother.inline_note(id="in:1", original_id="2")
        clipping = mother.clipping(id="1", inline_notes=[inline_note])
        book = mother.book(clippings=[clipping])

        result = book.unlink_inline_note(clipping_id="77", inline_note_id="in:1")

        assert isinstance(result, DomainError)
        assert str(result) == "Clipping with id 77 not found"

    def test_return_error_if_cant_find_inline_note(self, mother):
        inline_note = mother.inline_note(id="in:1", original_id="2")
        clipping = mother.clipping(id="1", inline_notes=[inline_note])
        book = mother.book(clippings=[clipping])

        result = book.unlink_inline_note(clipping_id="1", inline_note_id="in:77")

        assert isinstance(result, DomainError)
        assert str(result) == "Inline note with id in:77 not found"

    def test_return_error_if_note_is_not_autolinked(self, mother):
        inline_note = mother.inline_note(
            id="in:1", original_id="42", automatically_linked=False
        )
        clipping = mother.clipping(
            id="1", type=ClippingType.HIGHLIGHT, inline_notes=[inline_note]
        )
        book = mother.book(clippings=[clipping])

        result = book.unlink_inline_note(clipping_id="1", inline_note_id="in:1")

        assert isinstance(result, DomainError)
        assert str(result) == "Can't restore not autolinked note"

    def test_unlinked_note_must_be_saved_as_unlinked_note_type_and_properly_ordered(
        self, mother
    ):
        inline_note = mother.inline_note(
            id="in:1", original_id="42", automatically_linked=True
        )
        clipping = mother.clipping(
            id="1",
            page=(-1, -1),
            location=(42, 52),
            type=ClippingType.HIGHLIGHT,
            inline_notes=[inline_note],
        )
        another_clipping = mother.clipping(
            id="2", page=(-1, -1), location=(100, 200), type=ClippingType.HIGHLIGHT
        )
        book = mother.book(clippings=[clipping, another_clipping])

        result = book.unlink_inline_note(clipping_id="1", inline_note_id="in:1")

        assert result is None
        assert len(book.clippings) == 3
        unlinked_note = book.get_clipping("42")
        assert unlinked_note.type == ClippingType.UNLINKED_NOTE
        assert [cl.id for cl in book.clippings] == ["1", "42", "2"]


class TestRemoveClipping:
    def test_remove_clipping(self, mother):
        clipping = mother.clipping(id="1")
        book = mother.book(clippings=[clipping])

        book.remove_clipping(clipping)

        assert book.clippings == []
        assert book.get_clipping("1") is None

    def test_do_nothing_if_clipping_not_found(self, mother):
        clipping = mother.clipping(id="1")
        book = mother.book(clippings=[clipping])

        book.remove_clipping(mother.clipping(id="2"))

        assert book.clippings == [clipping]
