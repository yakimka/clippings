from unittest.mock import create_autospec

import pytest

from clippings.users.ports import PasswordHasherABC


@pytest.fixture()
def hasher_mock():
    return create_autospec(PasswordHasherABC, spec_set=True, instance=True)


def test_set_password_updates_hashed_password(mother, hasher_mock):
    password = "secure_password"
    hasher_mock.hash.return_value = "hashed_secure_password"
    sut = mother.user()

    sut.set_password(password, hasher_mock)

    assert sut.hashed_password == "hashed_secure_password"
    hasher_mock.hash.assert_called_once_with(password)


def test_check_password_returns_true_when_password_is_correct(mother, hasher_mock):
    password = "secure_password"
    sut = mother.user(hashed_password="hashed_secure_password")
    hasher_mock.verify.return_value = True

    result = sut.check_password(password, hasher_mock)

    assert result is True
    hasher_mock.verify.assert_called_once_with(password, "hashed_secure_password")


def test_check_password_returns_false_when_password_is_incorrect(mother, hasher_mock):
    password = "secure_password"
    sut = mother.user(hashed_password="hashed_secure_password")
    hasher_mock.verify.return_value = False

    result = sut.check_password(password, hasher_mock)

    assert result is False
    hasher_mock.verify.assert_called_once_with(password, "hashed_secure_password")


def test_check_password_returns_false_when_no_hashed_password(mother, hasher_mock):
    password = "secure_password"
    sut = mother.user(hashed_password=None)

    result = sut.check_password(password, hasher_mock)

    assert result is False
    hasher_mock.verify.assert_not_called()
