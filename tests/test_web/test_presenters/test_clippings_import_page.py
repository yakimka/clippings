import pytest

from clippings.web.presenters.book.clippings_import_page import (
    ClippingsImportPagePresenter,
    ImportPageDTO,
)
from clippings.web.presenters.dtos import PresenterResult
from clippings.web.presenters.urls import urls_manager


@pytest.fixture()
def make_sut():
    def _make_sut():
        return ClippingsImportPagePresenter(urls_manager)

    return _make_sut


async def test_present_should_return_presenter_result(make_sut):
    sut = make_sut()

    result = await sut.present()

    assert isinstance(result, PresenterResult)
    assert isinstance(result.data, ImportPageDTO)
    assert isinstance(result.render(), str)
