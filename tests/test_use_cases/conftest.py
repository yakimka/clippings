import pytest

from clippings.users.ports import PasswordHasherABC


@pytest.fixture()
def dummy_password_hasher():
    class DummyPasswordHasher(PasswordHasherABC):
        def hash(self, password: str) -> str:
            return f"{password}_hashed"

        def verify(self, password: str, hashed_password: str) -> bool:
            return self.hash(password) == hashed_password

    return DummyPasswordHasher()
