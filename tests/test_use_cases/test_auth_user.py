import pytest

from clippings.users.exceptions import AuthError
from clippings.users.use_cases.auth import AuthenticateUserUseCase, AuthUserDTO


@pytest.fixture()
def password_hasher(dummy_password_hasher):
    return dummy_password_hasher


@pytest.fixture()
def make_sut(memory_users_storage, password_hasher):
    def _make_sut():
        return AuthenticateUserUseCase(memory_users_storage, password_hasher)

    return _make_sut


async def test_authenticate_user_success(
    make_sut, memory_users_storage, password_hasher, mother
):
    sut = make_sut()
    user = mother.user(nickname="valid_nickname", id="user_id")
    user.set_password("valid_password", password_hasher)
    await memory_users_storage.add(user)

    result = await sut.execute(nickname="valid_nickname", password="valid_password")

    assert isinstance(result, AuthUserDTO)
    assert result.id == "user_id"
    assert result.nickname == "valid_nickname"


async def test_authenticate_user_user_not_found(
    make_sut, memory_users_storage, password_hasher, mother
):
    sut = make_sut()
    user = mother.user(nickname="valid_nickname", id="user_id")
    user.set_password("password", password_hasher)
    await memory_users_storage.add(user)

    result = await sut.execute(nickname="invalid_nickname", password="password")

    assert isinstance(result, AuthError)
    assert str(result) == "User not found"


async def test_authenticate_user_invalid_password(
    make_sut, memory_users_storage, password_hasher, mother
):
    sut = make_sut()
    user = mother.user(nickname="valid_nickname", id="user_id")
    user.set_password("password", password_hasher)
    await memory_users_storage.add(user)

    result = await sut.execute(nickname="valid_nickname", password="invalid_password")

    assert isinstance(result, AuthError)
    assert str(result) == "Invalid password"
