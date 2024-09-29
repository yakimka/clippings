from typing import Literal


def image_or_default(image_url: str | None, size: Literal["small", "big"]) -> str:
    return image_url or f"/static/img/no-cover-{size}.jpg"
