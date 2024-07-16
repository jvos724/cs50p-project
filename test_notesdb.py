import pytest
from notesdb import NotesDB
from note import Note


@pytest.fixture
def db():
    db_instance = NotesDB()
    yield db_instance
    db_instance.close()


@pytest.fixture
def test_notes():
    return [
        Note(name="Note1", tags=["tag1", "tag2"], content=["This is the first note."]),
        Note(name="Note2", tags=["tag1", "tag2"], content=["This is the second note."]),
        Note(name="Note3", tags=["tag1", "tag2"], content=["This is the third note."]),
    ]


def test_add_and_get_notes(db, test_notes):
    db.add(test_notes)

    notes = db.get()
    assert len(notes) == 3
    assert notes[0].name == "Note1"
    assert notes[1].name == "Note2"
    assert notes[2].name == "Note3"


def test_get_most_recent_notes(db, test_notes):
    db.add(test_notes)

    recent_notes = db.get(n=2)
    assert len(recent_notes) == 2
    assert recent_notes[0].name == "Note2"
    assert recent_notes[1].name == "Note3"


def test_search_notes(db, test_notes):
    db.add(test_notes)

    search_results = db.search("Note1")
    assert len(search_results) == 1
    assert search_results[0].name == "Note1"

    search_results = db.search("tag1")
    assert len(search_results) == 3


def test_search_empty_query(db):
    with pytest.raises(ValueError):
        db.search("")
