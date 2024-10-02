from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent


settings = Dynaconf(
    envvar_prefix="CLP",
    settings_files=[BASE_DIR.parent / "settings.yaml"],
    environments=True,
    load_dotenv=True,
)


@dataclass
class MongoSettings:
    uri: str

    @classmethod
    def create_from_config(cls) -> MongoSettings:
        return cls(uri=settings.mongo.uri)


@dataclass
class AdaptersSettings:
    books_storage: Literal["mongo", "mock", "notset"]
    users_storage: Literal["mongo", "mock", "notset"]
    deleted_hash_storage: Literal["mongo", "mock", "notset"]
    book_info_client: Literal["mock", "google", "notset"]

    @classmethod
    def create_from_config(cls) -> AdaptersSettings:
        adapters_conf = settings.get("adapters") or {}
        return cls(
            books_storage=adapters_conf.get("books_storage") or "notset",
            users_storage=adapters_conf.get("users_storage") or "notset",
            deleted_hash_storage=adapters_conf.get("deleted_hash_storage") or "notset",
            book_info_client=adapters_conf.get("book_info_client") or "notset",
        )

    def has_value(self, value: str) -> bool:
        for field in fields(self):  # noqa: SIM110
            if getattr(self, field.name) == value:
                return True
        return False

    @classmethod
    def defaults_for_web(cls) -> AdaptersSettings:
        return cls(
            books_storage="mongo",
            users_storage="mongo",
            deleted_hash_storage="mongo",
            book_info_client="google",
        )

    @classmethod
    def defaults_for_cli(cls) -> AdaptersSettings:
        return cls.defaults_for_web()

    def set_defaults(self, defaults: AdaptersSettings) -> None:
        for field in fields(self):
            if getattr(self, field.name) == "notset":
                new_value = getattr(defaults, field.name)
                if new_value in ("notset", None):
                    raise ValueError(f"Please provide a value for {field.name}")
                setattr(self, field.name, new_value)


@dataclass(kw_only=True)
class GoogleBooksApi:
    timeout: int = 1
    api_key: str | None = None

    @classmethod
    def create_from_config(cls) -> GoogleBooksApi:
        google_conf = settings.get("google_books_api") or {}
        params = {}
        if timeout := google_conf.get("timeout"):
            params["timeout"] = timeout
        if api_key := google_conf.get("api_key"):
            params["api_key"] = api_key
        return cls(**params)


@dataclass
class InfrastructureSettings:
    adapters: AdaptersSettings
    mongo: MongoSettings | None
    google_books_api: GoogleBooksApi | None

    @classmethod
    def create_from_config(cls, defaults: AdaptersSettings) -> InfrastructureSettings:
        mongo = google_books_api = None
        adapters = AdaptersSettings.create_from_config()
        adapters.set_defaults(defaults)
        if adapters.has_value("mongo"):
            mongo = MongoSettings.create_from_config()
        if adapters.has_value("google"):
            google_books_api = GoogleBooksApi.create_from_config()
        return cls(adapters=adapters, mongo=mongo, google_books_api=google_books_api)
