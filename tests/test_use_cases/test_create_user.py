import pytest

from clippings.seedwork.exceptions import DomainError
from clippings.users.adapters.id_generators import user_id_generator
from clippings.users.use_cases.create_user import CreateUserUseCase, UserToCreateDTO


@pytest.fixture()
def password_hasher(dummy_password_hasher):
    return dummy_password_hasher


@pytest.fixture()
def make_sut(memory_users_storage, password_hasher):
    def _make_sut():
        return CreateUserUseCase(
            memory_users_storage, user_id_generator, password_hasher
        )

    return _make_sut


async def test_successfully_add_user(make_sut, memory_users_storage, password_hasher):
    sut = make_sut()
    user_to_create = UserToCreateDTO(nickname="mario", password="luigisucks")

    user_id = await sut.execute(user_to_create)

    created_user = await memory_users_storage.get(user_id)
    assert created_user.id == user_id
    assert password_hasher.verify("luigisucks", created_user.hashed_password)


async def test_cant_add_user_with_same_nickname(make_sut, memory_users_storage, mother):
    sut = make_sut()
    await memory_users_storage.add(mother.user(nickname="mario"))
    user_to_create = UserToCreateDTO(nickname="mario", password="luigisucks")

    result = await sut.execute(user_to_create)

    assert isinstance(result, DomainError)
    assert str(result) == "User with nickname 'mario' already exists"


async def test_user_password_must_be_at_least_8_characters_long(make_sut):
    sut = make_sut()
    user_to_create = UserToCreateDTO(nickname="mario", password="short")

    result = await sut.execute(user_to_create)

    assert isinstance(result, DomainError)
    assert str(result) == "Password must be at least 8 characters long"
