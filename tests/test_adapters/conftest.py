from __future__ import annotations

import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@pytest.fixture()
async def mongo_db() -> AsyncIOMotorDatabase:
    uri = os.getenv("TEST_MONGO_URI")
    if uri is None:
        raise ValueError("TEST_MONGO_URI is not set")

    client = AsyncIOMotorClient(uri)
    yield client.test_db
    await client.drop_database("test_db")
