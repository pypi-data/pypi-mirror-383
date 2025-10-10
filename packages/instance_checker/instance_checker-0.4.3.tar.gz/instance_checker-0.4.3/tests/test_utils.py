import os
import sys
from pathlib import Path
from unittest import mock

import pytest
from psutil import NoSuchProcess

from src.instance_checker.utils import CountHelper


@pytest.fixture
def helper():
    with mock.patch("src.instance_checker.utils.gettempdir", return_value="/tmp/locks"):
        yield CountHelper(lock_dir="/tmp/locks")


TEST_IDENTIFIER = "my_app"


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_no_matches(mock_process_iter):
    mock_process_iter.return_value = []

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_one_match(mock_process_iter):
    mock_process_iter.return_value = [
        mock.MagicMock(
            cmdline=mock.MagicMock(return_value=["/usr/bin/python", "my_app.py"]),
        ),
        mock.MagicMock(
            cmdline=mock.MagicMock(return_value=["/bin/sh", "other_script.sh"]),
        ),
    ]

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 1


@mock.patch("src.instance_checker.utils.process_iter")
def test_process_count_raised(mock_process_iter):
    mock_process_iter.return_value = [
        mock.MagicMock(cmdline=mock.MagicMock(side_effect=NoSuchProcess(123))),
    ]

    count = CountHelper.process_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.os.walk")
def test_pid_file_count_no_files(mock_walk, helper):
    mock_walk.return_value = [(".", [], [])]

    count = helper.pid_file_count(TEST_IDENTIFIER)
    assert count == 0


@mock.patch("src.instance_checker.utils.os.walk")
def test_pid_file_count_one_file(mock_walk, helper):
    mock_walk.return_value = [("/tmp/locks", [], ["my_app.lock.0"])]

    count = helper.pid_file_count(TEST_IDENTIFIER)
    assert count == 1


@mock.patch("src.instance_checker.utils.os.walk")
def test_get_pid_file(mock_walk, helper):
    mock_walk.return_value = [
        (
            "/tmp/locks",
            [],
            ["my_app.lock.0", "file.71fc8e82be524ebbba98df6564de5008.lock.12345"],
        ),
    ]

    file = helper.get_pid_file(identifier="file.")
    assert str(file.name) == "file.71fc8e82be524ebbba98df6564de5008.lock.12345"


@mock.patch("src.instance_checker.utils.os.walk")
def test_get_pid_file_none(mock_walk, helper):
    mock_walk.return_value = [
        (
            "/tmp/locks",
            [],
            ["my_app.lock.0", "my_app.lock.1"],
        ),
    ]

    file = helper.get_pid_file(identifier="file.")
    assert file is None


@pytest.mark.skipif(sys.platform == "win32", reason="tests for linux only")
@mock.patch("pathlib.Path.open", new_callable=mock.mock_open)
@mock.patch("src.instance_checker.utils.os.lockf")
def test_acquire_pid_file(mock_lockf, mock_open, helper):
    identifier = "my_app"
    pid = os.getpid()
    filename = f"{identifier}.lock.{pid}"
    path = Path(helper.lock_dir) / filename

    result_path, _ = helper.acquire_pid_file(filename=filename)

    assert result_path == path
    mock_open.assert_called_once_with(mode="x")
    assert mock_lockf.mock_calls[0].args[1] == os.F_LOCK
    assert mock_lockf.mock_calls[0].args[2] == 0


@pytest.mark.skipif(sys.platform == "win32", reason="tests for linux only")
@mock.patch("pathlib.Path.open", new_callable=mock.mock_open)
@mock.patch("src.instance_checker.utils.os.lockf")
def test_is_released_pid_file_true(mock_lockf, mock_open, helper):
    filename = "my_app.lock.12345"

    result = helper.is_released_pid_file(filename)

    assert result is True
    mock_open.assert_called_once_with(mode="r")
    assert mock_lockf.call_count == 1
    assert mock_lockf.mock_calls[0].args[1] == 3
    assert mock_lockf.mock_calls[0].args[2] == 0


@pytest.mark.skipif(sys.platform == "win32", reason="tests for linux only")
@mock.patch("pathlib.Path.open", new_callable=mock.mock_open)
@mock.patch("src.instance_checker.utils.os.lockf", side_effect=OSError())
def test_is_released_pid_file_false(mock_lockf, mock_open, helper):
    filename = "my_app.lock.12345"

    result = helper.is_released_pid_file(filename)

    assert result is False
