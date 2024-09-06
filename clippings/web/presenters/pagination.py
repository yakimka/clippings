from typing import Protocol

from clippings.web.presenters.dtos import PaginationDTO, PaginationItemDTO


class PaginationCalculator(Protocol):
    def __call__(
        self, current_page: int, total_items: int, on_page: int, books_page_url: str
    ) -> PaginationDTO:
        pass


def classic_pagination_calculator(
    current_page: int, total_items: int, on_page: int, books_page_url: str
) -> PaginationDTO:
    total_pages = (total_items + on_page - 1) // on_page

    if total_pages <= 1:
        return PaginationDTO(current_page=1, total_pages=1, items=[])

    if current_page > total_pages:
        current_page = total_pages

    total_range = range(1, total_pages + 1)
    if len(total_range) > 9:
        left = max(2, current_page - 3)
        right = min(total_pages - 1, current_page + 3)
        if right - left < 6:
            if left == 2:
                right = min(total_pages - 1, left + 6)
            else:
                left = max(2, right - 6)
        page_numbers = [1] + list(range(left, right + 1)) + [total_pages]
    else:
        page_numbers = list(total_range)

    return PaginationDTO(
        current_page=current_page,
        total_pages=total_pages,
        items=[
            PaginationItemDTO(
                text=str(i),
                url=(
                    None
                    if i == current_page
                    else f"{books_page_url}?page={i}&on_page={on_page}"
                ),
            )
            for i in page_numbers
        ],
    )
