from unittest.mock import patch

import pytest
from picodi import registry

from clippings.cli.run_command import main as run_command_main
from clippings.deps import get_mock_users_storage, get_users_storage


@pytest.fixture(autouse=True)
async def _override_deps():
    with registry.override(get_users_storage, get_mock_users_storage):
        yield


@pytest.mark.parametrize(
    "command_name,args,expected_message",
    [
        (
            "create_user",
            ["test_user", "--password=test_password"],
            "User test_user created with id",
        ),
    ],
)
async def test_run_commands(command_name, args, expected_message, capsys):
    with patch("sys.argv", ["clippings.cli", command_name, *args]):
        with pytest.raises(SystemExit, match="0"):
            await run_command_main()

    captured = capsys.readouterr()
    assert expected_message in captured.out
    assert captured.err == ""
