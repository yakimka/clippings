import pytest

from clippings.web.presenters.dtos import PaginationDTO, PaginationItemDTO
from clippings.web.presenters.pagination import classic_pagination_calculator


@pytest.fixture()
def make_sut():
    def _make_sut():
        return classic_pagination_calculator

    return _make_sut


def test_returns_pagination_with_one_page_if_total_items_less_than_on_page(make_sut):
    sut = make_sut()

    result = sut(current_page=1, total_items=5, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(current_page=1, total_pages=1, items=[])


def test_correctly_calculates_pagination_for_multiple_pages(make_sut):
    sut = make_sut()

    result = sut(current_page=2, total_items=25, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(
        current_page=2,
        total_pages=3,
        items=[
            PaginationItemDTO(text="1", url="/books?page=1&on_page=10"),
            PaginationItemDTO(text="2", url=None),
            PaginationItemDTO(text="3", url="/books?page=3&on_page=10"),
        ],
    )


def test_adjusts_current_page_if_it_exceeds_total_pages(make_sut):
    sut = make_sut()

    result = sut(current_page=5, total_items=30, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(
        current_page=3,
        total_pages=3,
        items=[
            PaginationItemDTO(text="1", url="/books?page=1&on_page=10"),
            PaginationItemDTO(text="2", url="/books?page=2&on_page=10"),
            PaginationItemDTO(text="3", url=None),
        ],
    )


def test_handles_large_number_of_pages_by_collapsing_pagination(make_sut):
    sut = make_sut()

    result = sut(current_page=6, total_items=110, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(
        current_page=6,
        total_pages=11,
        items=[
            PaginationItemDTO(text="1", url="/books?page=1&on_page=10"),
            PaginationItemDTO(text="3", url="/books?page=3&on_page=10"),
            PaginationItemDTO(text="4", url="/books?page=4&on_page=10"),
            PaginationItemDTO(text="5", url="/books?page=5&on_page=10"),
            PaginationItemDTO(text="6", url=None),
            PaginationItemDTO(text="7", url="/books?page=7&on_page=10"),
            PaginationItemDTO(text="8", url="/books?page=8&on_page=10"),
            PaginationItemDTO(text="9", url="/books?page=9&on_page=10"),
            PaginationItemDTO(text="11", url="/books?page=11&on_page=10"),
        ],
    )


def test_handles_large_number_of_pages_left_by_collapsing_pagination(make_sut):
    sut = make_sut()

    result = sut(current_page=90, total_items=1000, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(
        current_page=90,
        total_pages=100,
        items=[
            PaginationItemDTO(text="1", url="/books?page=1&on_page=10"),
            PaginationItemDTO(text="87", url="/books?page=87&on_page=10"),
            PaginationItemDTO(text="88", url="/books?page=88&on_page=10"),
            PaginationItemDTO(text="89", url="/books?page=89&on_page=10"),
            PaginationItemDTO(text="90", url=None),
            PaginationItemDTO(text="91", url="/books?page=91&on_page=10"),
            PaginationItemDTO(text="92", url="/books?page=92&on_page=10"),
            PaginationItemDTO(text="93", url="/books?page=93&on_page=10"),
            PaginationItemDTO(text="100", url="/books?page=100&on_page=10"),
        ],
    )


def test_handles_large_number_of_pages_right_by_collapsing_pagination(make_sut):
    sut = make_sut()

    result = sut(current_page=10, total_items=1000, on_page=10, books_page_url="/books")

    assert result == PaginationDTO(
        current_page=10,
        total_pages=100,
        items=[
            PaginationItemDTO(text="1", url="/books?page=1&on_page=10"),
            PaginationItemDTO(text="7", url="/books?page=7&on_page=10"),
            PaginationItemDTO(text="8", url="/books?page=8&on_page=10"),
            PaginationItemDTO(text="9", url="/books?page=9&on_page=10"),
            PaginationItemDTO(text="10", url=None),
            PaginationItemDTO(text="11", url="/books?page=11&on_page=10"),
            PaginationItemDTO(text="12", url="/books?page=12&on_page=10"),
            PaginationItemDTO(text="13", url="/books?page=13&on_page=10"),
            PaginationItemDTO(text="100", url="/books?page=100&on_page=10"),
        ],
    )


@pytest.mark.parametrize("current_page", list(range(1, 101)))
def test_always_render_nine_pages_if_total_pages_is_gt8(make_sut, current_page):
    sut = make_sut()

    result = sut(
        current_page=current_page, total_items=1000, on_page=10, books_page_url="/books"
    )

    assert len(result.items) == 9
