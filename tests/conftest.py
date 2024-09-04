import pytest

from clippings.test.object_mother import ObjectMother


@pytest.fixture()
def mother():
    return ObjectMother()
