import pytest

from clippings.users.adapters.password_hashers import PBKDF2PasswordHasher


@pytest.fixture()
def make_sut():
    def _make_sut(iterations=50_000, salt_length=16):
        return PBKDF2PasswordHasher(iterations=iterations, salt_length=salt_length)

    return _make_sut


def test_hash_generates_valid_format(make_sut):
    sut = make_sut()
    password = "password123"  # noqa: S105

    hashed_password = sut.hash(password)

    assert len(hashed_password.split(":")) == 2


def test_verify_returns_true_for_correct_password(make_sut):
    sut = make_sut()
    password = "password123"  # noqa: S105
    hashed_password = sut.hash(password)

    result = sut.verify(password, hashed_password)

    assert result is True


def test_verify_returns_false_for_incorrect_password(make_sut):
    sut = make_sut()
    hashed_password = sut.hash("password123")

    result = sut.verify("wrong_password", hashed_password)

    assert result is False


def test_verify_returns_false_for_malformed_hashed_password(make_sut):
    sut = make_sut()

    result = sut.verify("password123", "malformed_hash")

    assert result is False
