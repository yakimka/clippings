import pytest

from clippings.seedwork.exceptions import DomainError
from clippings.users.adapters.id_generators import user_id_generator
from clippings.users.adapters.storages import MockUsersStorage
from clippings.users.use_cases.create_user import CreateUserUseCase, UserToCreateDTO


@pytest.fixture()
def users_storage():
    return MockUsersStorage()


@pytest.fixture()
def password_hasher(dummy_password_hasher):
    return dummy_password_hasher


@pytest.fixture()
def make_sut(users_storage, password_hasher):
    def _make_sut():
        return CreateUserUseCase(users_storage, user_id_generator, password_hasher)

    return _make_sut


async def test_successfully_add_user(make_sut, users_storage, password_hasher):
    sut = make_sut()
    user_to_create = UserToCreateDTO(nickname="mario", password="luigisucks")

    user_id = await sut.execute(user_to_create)

    created_user = await users_storage.get(user_id)
    assert created_user.id == user_id
    assert password_hasher.verify("luigisucks", created_user.hashed_password)


async def test_cant_add_user_with_same_nickname(make_sut, users_storage, mother):
    sut = make_sut()
    await users_storage.add(mother.user(nickname="mario"))
    user_to_create = UserToCreateDTO(nickname="mario", password="luigisucks")

    result = await sut.execute(user_to_create)

    assert isinstance(result, DomainError)
    assert str(result) == "User with nickname 'mario' already exists"
