import pytest

from clippings.cli.controllers import CreateUserController


@pytest.fixture()
def make_sut(memory_users_storage, dummy_password_hasher):
    def _make_sut():
        return CreateUserController(
            users_storage=memory_users_storage, password_hasher=dummy_password_hasher
        )

    return _make_sut


async def test_create_user_success(make_sut, memory_users_storage):
    sut = make_sut()

    result = await sut.execute(nickname="test_user", password="test_password")

    assert isinstance(result.message, str)
    assert result.exit_code == 0
    created_user = await memory_users_storage.get_by_nickname("test_user")
    assert created_user.nickname == "test_user"
    assert created_user.hashed_password == "test_password_hashed"


async def test_create_user_failure_due_to_domain_error(make_sut):
    sut = make_sut()

    # must return error because password is too short
    result = await sut.execute(nickname="test_user", password="1234")

    assert "password must be at least" in result.message.lower()
    assert result.exit_code == 1
