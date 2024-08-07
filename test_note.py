import pytest
from unittest.mock import patch, MagicMock
from note import Note


@pytest.fixture
def test_note():
    return Note(
        name="Test Note", tags=["tag1", "tag2"], content=["Line 1", "Line 2"], id=1
    )


# test that all Note attributes initialize correctly
def test_note_initialization(test_note):
    assert test_note.id == 1
    assert test_note.name == "Test Note"
    assert test_note.tags == ["tag1", "tag2"]
    assert test_note.content == ["Line 1", "Line 2"]


# test Note.id set/get
def test_note_id_property(test_note):
    test_note.id = 10
    assert test_note.id == 10

    test_note.id = 0
    assert test_note.id == 0


# test Note.id=0 default
def test_note_undef_id_is_zero():
    undef_id_note = Note(
        name="Test Note", tags=["tag1", "tag2"], content=["Line 1", "Line 2"]
    )

    assert undef_id_note.id == 0


# test Note.name set/get
def test_note_name_property(test_note):
    with pytest.raises(ValueError):
        test_note.name = ""

    test_note.name = "Updated Note"
    assert test_note.name == "Updated Note"


# test Note.tags set/get
def test_note_tags_property(test_note):
    with pytest.raises(ValueError):
        test_note.tags = [""]

    test_note.tags = ["new1", "new2"]
    assert test_note.tags == ["new1", "new2"]


# test Note.content set/get
def test_note_content_property(test_note):
    with pytest.raises(ValueError):
        test_note.content = [""]

    test_note.content = ["New line 1", "New line 2"]
    assert test_note.content == ["New line 1", "New line 2"]


# test Note rich print method
def test_rich_console(test_note):
    from rich.console import Console

    console = Console(record=True)

    with console.capture() as capture:
        for segment in test_note.__rich_console__(console, None):
            console.print(segment)
    output = capture.get()

    assert "NOTE #1" in output
    assert "END NOTE #1" in output
    assert "#tag1 #tag2" in output
    assert "Test Note" in output
    assert "Line 1" in output
    assert "Line 2" in output


# test Note.confirm() interactive method
@patch("rich.prompt.Confirm.ask")
def test_confirm(mock_ask, test_note):
    mock_ask.return_value = True
    assert test_note.confirm() is True

    mock_ask.return_value = False
    assert test_note.confirm() is False


# test Note.new() interactive creation
@patch("rich.prompt.Prompt.ask")
@patch("project.eof_input")
@patch("project.parse_tags")
def test_new(mock_parse_tags, mock_eof_input, mock_prompt_ask):
    mock_prompt_ask.side_effect = ["Test Note", "tag1,tag2"]
    mock_parse_tags.return_value = ["tag1", "tag2"]
    mock_eof_input.return_value = ["Line 1", "Line 2"]

    note = Note.new()

    assert note.name == "Test Note"
    assert note.tags == ["tag1", "tag2"]
    assert note.content == ["Line 1", "Line 2"]


# test Note.new() interactive creation with invalid inputs
# TODO: implement


# test Note.from_sql() method
def test_from_sql():
    row = (1, "Test Note", "tag1,tag2", "Line 1\nLine 2")

    note = Note.from_sql(row)

    assert note.id == 1
    assert note.name == "Test Note"
    assert note.tags == ["tag1", "tag2"]
    assert note.content == ["Line 1", "Line 2"]


# test Note.from_sql() returns None for invalid entry
def test_from_sql_invalid_db():
    row = (1, "", "", "")

    note = Note.from_sql(row)

    assert note == None
