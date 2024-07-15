import pytest
from unittest.mock import patch, MagicMock

from project import *


# TESTING get_args()


def test_new_command_without_name(monkeypatch):
    test_args = ["sc", "new"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "new"
    assert args.name is None


def test_new_command_with_name(monkeypatch):
    test_args = ["sc", "new", "my_note"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "new"
    assert args.name == "my_note"


def test_new_command_alias(monkeypatch):
    test_args = ["sc", "n", "my_note"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "n"
    assert args.name == "my_note"


def test_list_command_without_num(monkeypatch):
    test_args = ["sc", "list"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "list"
    assert args.num == 0


def test_list_command_with_num(monkeypatch):
    test_args = ["sc", "list", "5"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "list"
    assert args.num == "5"


def test_list_command_alias(monkeypatch):
    test_args = ["sc", "l", "5"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "l"
    assert args.num == "5"


def test_search_command_without_query(monkeypatch):
    test_args = ["sc", "search"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "search"
    assert args.query is None


def test_search_command_with_query(monkeypatch):
    test_args = ["sc", "search", "tag1"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "search"
    assert args.query == "tag1"


def test_search_command_alias(monkeypatch):
    test_args = ["sc", "s", "tag1"]
    monkeypatch.setattr("sys.argv", test_args)
    args = get_args()
    assert args.mode == "s"
    assert args.query == "tag1"


# TESTING parse_tags()


@pytest.mark.parametrize(
    "input_str, expected_output",
    [
        ("tag1 tag2 tag3", ["tag1", "tag2", "tag3"]),
        ("tag1,tag2,tag3", ["tag1", "tag2", "tag3"]),
        ("#tag1#tag2#tag3", ["tag1", "tag2", "tag3"]),
        ("tag1, tag2 # tag3", ["tag1", "tag2", "tag3"]),
        ("  tag1 tag2 tag3  ", ["tag1", "tag2", "tag3"]),
        ("#tag1, tag2#", ["tag1", "tag2"]),
        ("", [""]),
        ("tag1##tag2,,tag3  tag4", ["tag1", "tag2", "tag3", "tag4"]),
    ],
)
def test_parse_tags(input_str, expected_output):
    assert parse_tags(input_str) == expected_output


# TESTING eof_input()


def test_eof_input():
    user_inputs = ["First line", "Second line", "Third line"]

    with patch("builtins.input", side_effect=user_inputs + [EOFError]):
        with patch("builtins.print"):
            result = eof_input()

    assert result == user_inputs
