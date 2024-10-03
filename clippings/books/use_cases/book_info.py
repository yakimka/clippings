from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx

from clippings.books.dtos import BookInfoSearchResultDTO
from clippings.books.ports import BookInfoClientABC


class MockBookInfoClient(BookInfoClientABC):
    def __init__(self) -> None:
        image_ids = [
            "N6EGEAAAQBAJ",
            "MoEO9onVftUC",
            "zFheDgAAQBAJ",
            "DkexBQAAQBAJ",
            "kYZHCgAAQBAJ",
        ]

        def make_google_books_img_urls(id: str, zoom: int) -> str:
            return (
                f"https://books.google.com/books/content?id={id}"
                f"&printsec=frontcover&img=1&zoom={zoom}"
            )

        self._images = [
            (None, None),
            *[
                (make_google_books_img_urls(id, 1), make_google_books_img_urls(id, 3))
                for id in image_ids
            ],
        ]

    async def get(
        self, title: str, author: str | None = None
    ) -> BookInfoSearchResultDTO | None:
        if "ч" in title:
            return None

        small_img, large_img = self._images[len(title) % len(self._images)]
        return BookInfoSearchResultDTO(
            isbns=[],
            title=title,
            authors=[author] if author else [],
            cover_image_small=small_img,
            cover_image_big=large_img,
        )


class GoogleBookInfoClient(BookInfoClientABC):
    def __init__(self, *, timeout: int, api_key: str | None) -> None:
        self._timeout = timeout
        self._api_key = api_key
        self._http_client: httpx.AsyncClient | None = None

    @property
    def _client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            params: dict | None = None
            if self._api_key:
                params = {"key": self._api_key}
            self._http_client = httpx.AsyncClient(
                base_url="https://www.googleapis.com/books/v1",
                timeout=self._timeout,
                params=params,
            )
        return self._http_client

    async def get(
        self, title: str, author: str | None = None
    ) -> BookInfoSearchResultDTO | None:
        query = f"intitle:{title}"
        if author:
            query = f"{query}+inauthor:{author}"
        resp = await self._client.get(
            "/volumes",
            params={
                "q": query,
                "fields": (
                    "items(volumeInfo(title,authors,imageLinks,industryIdentifiers))"
                ),
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("items"):
            return None

        for item in data["items"]:
            info = self._deserialize(item)
            if info and info.cover_image_small and info.cover_image_big:
                return info
        return None

    def _deserialize(self, data: dict) -> BookInfoSearchResultDTO | None:
        try:
            volume_info = data["volumeInfo"]
            thumbnail = volume_info["imageLinks"]["thumbnail"]
            title = volume_info["title"]
            authors = volume_info["authors"]
            isbns = []
            for identifier in volume_info.get("industryIdentifiers", []):
                if "isbn" in identifier["type"].lower():
                    isbns.append(identifier["identifier"])
        except KeyError:
            return None

        return BookInfoSearchResultDTO(
            isbns=isbns,
            title=title,
            authors=authors,
            cover_image_small=_replace_query_params(
                thumbnail, zoom="1", edge=None, source=None
            ),
            cover_image_big=_replace_query_params(
                thumbnail, zoom="3", edge=None, source=None
            ),
        )

    async def aclose(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None


def _replace_query_params(url: str, **params: str | None) -> str:
    url_parts = list(urlparse(url))
    query_params = parse_qs(url_parts[4])
    for param, new_value in params.items():
        if new_value is None:
            query_params.pop(param, None)
            continue
        query_params[param] = [new_value]
    url_parts[4] = urlencode(query_params, doseq=True)
    return urlunparse(url_parts)
