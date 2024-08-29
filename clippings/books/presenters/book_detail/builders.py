from clippings.books.entities import Book
from clippings.books.presenters.book_detail.dtos import (
    BookDetailDTO,
    BookInfoDTO,
    BookReviewDTO,
    ClippingDTO,
    InlineNoteDTO,
)
from clippings.books.presenters.dtos import ActionDTO
from clippings.books.presenters.urls import UrlsManager


class BookDetailBuilder:
    def __init__(self, book: Book, urls_manager: UrlsManager) -> None:
        self.book = book
        self.clippings_by_id = {clipping.id: clipping for clipping in book.clippings}
        self.inline_notes_by_id = {
            (cl.id, inl.id): inl for cl in book.clippings for inl in cl.inline_notes
        }
        self.urls_manager = urls_manager

    def detail_dto(self) -> BookDetailDTO:
        main_info_dto = self.main_info_dto()
        review_dto = self.review_dto()
        return BookDetailDTO(
            page_title=f"{self.book.title} Clippings",
            actions=[*main_info_dto.actions, *review_dto.actions],
            cover_url=main_info_dto.cover_url,
            title=main_info_dto.title,
            author=main_info_dto.author,
            rating=main_info_dto.rating,
            review=review_dto.review,
            notes_label="Notes",
            clippings=self.clippings_dtos(),
        )

    def clippings_dtos(self) -> list[ClippingDTO]:
        return [self.clipping_dto(clipping.id) for clipping in self.book.clippings]

    def clipping_dto(self, clipping_id: str) -> ClippingDTO:
        clipping = self.clippings_by_id[clipping_id]
        return ClippingDTO(
            content=clipping.content,
            type=clipping.type.value.capitalize(),
            page=f"Page: {"-".join(map(str, clipping.page))}",
            location=f"Loc: {"-".join(map(str, clipping.location))}",
            added_at=f"Added: {clipping.added_at.date().isoformat()}",
            inline_notes=self.inline_notes_dtos(clipping.id),
            actions=[
                ActionDTO(
                    id="inline_note_add",
                    label="add note",
                    url=self.urls_manager.build_url(
                        "inline_note_add",
                        book_id=self.book.id,
                        clipping_id=clipping.id,
                    ),
                ),
                ActionDTO(
                    id="clipping_update_form",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "clipping_update_form",
                        book_id=self.book.id,
                        clipping_id=clipping.id,
                    ),
                ),
                ActionDTO(
                    id="clipping_delete",
                    label="delete",
                    url=self.urls_manager.build_url(
                        "clipping_delete",
                        book_id=self.book.id,
                        clipping_id=clipping.id,
                    ),
                ),
            ],
        )

    def inline_notes_dtos(self, clipping_id: str) -> list[InlineNoteDTO]:
        clipping = self.clippings_by_id[clipping_id]
        return [
            self.inline_note_dto(clipping_id, inline_note.id)
            for inline_note in clipping.inline_notes
        ]

    def inline_note_dto(self, clipping_id: str, inline_note_id: str) -> InlineNoteDTO:
        inline_note = self.inline_notes_by_id[(clipping_id, inline_note_id)]

        inline_note_dto = InlineNoteDTO(
            id=inline_note.id,
            content=inline_note.content,
            actions=[
                ActionDTO(
                    id="inline_note_update_form",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "inline_note_update_form",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                ),
                ActionDTO(
                    id="inline_note_delete",
                    label="delete",
                    url=self.urls_manager.build_url(
                        "inline_note_delete",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                ),
            ],
        )
        if inline_note.automatically_linked:
            inline_note_dto.actions.append(
                ActionDTO(
                    id="inline_note_unlink",
                    label="unlink",
                    url=self.urls_manager.build_url(
                        "inline_note_unlink",
                        book_id=self.book.id,
                        clipping_id=clipping_id,
                        inline_note_id=inline_note.id,
                    ),
                )
            )
        return inline_note_dto

    def main_info_dto(self) -> BookInfoDTO:
        return BookInfoDTO(
            cover_url="https://placehold.co/400x600",
            title=self.book.title,
            author=f"by {self.book.author}",
            rating=(
                "No rating"
                if self.book.rating is None
                else f"Rating: {self.book.rating}/10"
            ),
            actions=[
                ActionDTO(
                    id="book_info_update_form",
                    label="edit",
                    url=self.urls_manager.build_url(
                        "book_info_update_form", book_id=self.book.id
                    ),
                )
            ],
        )

    def review_dto(self) -> BookReviewDTO:
        return BookReviewDTO(
            review=self.book.review,
            actions=[
                ActionDTO(
                    id="book_review_update_form",
                    label="edit" if self.book.review else "Add review",
                    url=self.urls_manager.build_url(
                        "book_review_update_form", book_id=self.book.id
                    ),
                ),
            ],
        )
