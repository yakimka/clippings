from typing import Protocol

from clippings.books.presenters.dtos import PaginationItemDTO


class PaginationPresenter(Protocol):
    def __call__(
        self, current_page: int, total_items: int, on_page: int, books_page_url: str
    ) -> list[PaginationItemDTO]:
        pass


def classic_pagination_presenter(
    current_page: int, total_items: int, on_page: int, books_page_url: str
) -> list[PaginationItemDTO]:
    total_pages = (total_items + on_page - 1) // on_page

    if total_pages == 1:
        return []

    page_numbers: range | list = range(1, total_pages + 1)
    if len(page_numbers) > 9:
        page_numbers = [1]
        if current_page > 5:
            page_numbers.append("...")
        page_numbers.extend(
            range(max(2, current_page - 4), min(current_page + 5, total_pages - 1))
        )
        if current_page < total_pages - 4:
            page_numbers.append("...")
        page_numbers.append(total_pages)
    return [
        PaginationItemDTO(
            text=str(i),
            url=(
                None
                if i == current_page
                else f"{books_page_url}?page={i}&on_page={on_page}"
            ),
        )
        for i in page_numbers
    ]
