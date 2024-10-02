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
    book_info_client: Literal["mock", "notset"]

    @classmethod
    def create_from_config(cls) -> AdaptersSettings:
        settings_adapters = settings.get("adapters", {})
        return cls(
            books_storage=settings_adapters.get("books_storage"),
            users_storage=settings_adapters.get("users_storage"),
            deleted_hash_storage=settings_adapters.get("deleted_hash_storage"),
            book_info_client=settings_adapters.get("book_info_client"),
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
            book_info_client="mock",
        )

    @classmethod
    def defaults_for_cli(cls) -> AdaptersSettings:
        return cls.defaults_for_web()

    def set_defaults(self, defaults: AdaptersSettings) -> None:
        for field in fields(self):
            if getattr(self, field.name) is None:
                new_value = getattr(defaults, field.name)
                if new_value == "notset":
                    raise ValueError(f"Please provide a value for {field.name}")
                setattr(self, field.name, new_value)


@dataclass
class InfrastructureSettings:
    adapters: AdaptersSettings
    mongo: MongoSettings | None

    @classmethod
    def create_from_config(cls, defaults: AdaptersSettings) -> InfrastructureSettings:
        mongo = None
        adapters = AdaptersSettings.create_from_config()
        adapters.set_defaults(defaults)
        if adapters.has_value("mongo"):
            mongo = MongoSettings.create_from_config()
        return cls(adapters=adapters, mongo=mongo)
