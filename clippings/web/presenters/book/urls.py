from clippings.web.presenters.dtos import UrlTemplateDTO


def make_book_urls(base_url: str = "/books") -> list[UrlTemplateDTO]:
    def make_template(template: str, *, add_closing_slash: bool = True) -> str:
        template = template.removesuffix("/")
        if add_closing_slash:
            template = f"{template}/"
        return f"{base_url.rstrip('/')}{template}"

    return [
        UrlTemplateDTO(
            id="clippings_import_page",
            template=make_template("/import"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_upload",
            template=make_template("/import"),
            method="post",
        ),
        UrlTemplateDTO(
            id="clippings_export",
            template=make_template("/export"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clippings_restore",
            template=make_template("/restore"),
            method="post",
        ),
        UrlTemplateDTO(
            id="book_delete",
            template=make_template("/{book_id}"),
            method="delete",
        ),
        UrlTemplateDTO(
            id="book_detail_page",
            template=make_template("/{book_id}"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_info",
            template=make_template("/{book_id}/info"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_info_update",
            template=make_template("/{book_id}/info"),
            method="put",
        ),
        UrlTemplateDTO(
            id="book_info_update_form",
            template=make_template("/{book_id}/info/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_list_page",
            template=make_template(""),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_review",
            template=make_template("/{book_id}/review"),
            method="get",
        ),
        UrlTemplateDTO(
            id="book_review_update",
            template=make_template("/{book_id}/review"),
            method="put",
        ),
        UrlTemplateDTO(
            id="book_review_update_form",
            template=make_template("/{book_id}/review/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_list",
            template=make_template("/{book_id}/clippings"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_delete",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="delete",
        ),
        UrlTemplateDTO(
            id="clipping_detail",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="get",
        ),
        UrlTemplateDTO(
            id="clipping_update",
            template=make_template("/{book_id}/clippings/{clipping_id}"),
            method="put",
        ),
        UrlTemplateDTO(
            id="clipping_update_form",
            template=make_template("/{book_id}/clippings/{clipping_id}/edit"),
            method="get",
        ),
        UrlTemplateDTO(
            id="inline_note_add",
            template=make_template("/{book_id}/clippings/{clipping_id}/inline_notes"),
            method="post",
        ),
        UrlTemplateDTO(
            id="inline_note_add_form",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/add"
            ),
            method="get",
        ),
        UrlTemplateDTO(
            id="inline_note_delete",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}"
            ),
            method="delete",
        ),
        UrlTemplateDTO(
            id="inline_note_unlink",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/"
                "inline_notes/{inline_note_id}/unlink"
            ),
            method="post",
        ),
        UrlTemplateDTO(
            id="inline_note_update",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}"
            ),
            method="put",
        ),
        UrlTemplateDTO(
            id="inline_note_update_form",
            template=make_template(
                "/{book_id}/clippings/{clipping_id}/inline_notes/{inline_note_id}/edit"
            ),
            method="get",
        ),
        UrlTemplateDTO(
            id="deleted_hash_clear",
            template=make_template("/deleted_hashes/clear"),
            method="post",
        ),
    ]
