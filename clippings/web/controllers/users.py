from clippings.web.controllers.responses import HTMLResponse, Response
from clippings.web.presenters.user.settings_page import SettingsPagePresenter


class RenderSettingsPageController:
    async def fire(self) -> Response:
        presenter = SettingsPagePresenter()
        result = await presenter.present()
        return HTMLResponse.from_presenter_result(result)
