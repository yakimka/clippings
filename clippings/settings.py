from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
    def create(cls) -> MongoSettings:
        return cls(uri=settings.mongo.uri)


@dataclass
class InfrastructureSettings:
    mongo: MongoSettings

    @classmethod
    def create(cls) -> InfrastructureSettings:
        return cls(mongo=MongoSettings.create())
