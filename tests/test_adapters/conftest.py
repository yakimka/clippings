from __future__ import annotations

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from picodi.helpers import enter

from clippings.deps import get_mongo_database


@pytest.fixture()
async def mongo_db(mongo_client, mongo_test_db_name) -> AsyncIOMotorDatabase:
    async with enter(get_mongo_database) as db:
        yield db
