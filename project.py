#!/home/jeff/Dev/cs50p/project/.venv/bin/python
import argparse
import os
import random
import re
import sqlite3
import string
import sys
from datetime import datetime

from rich import print
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule

# default db file if none is specified
# TODO: add support for Windows path here
DB_FILE = "~/.local/share/cb/notes.db"


class NotesDB:
    def __init__(self, db=DB_FILE):
        self.db = db

    def add(self, notes):
        db_path = os.path.expanduser(self.db)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY key,
            name TEXT NOT NULL,
            tags TEXT,
            content TEXT
            )
            """
        )

        for note in notes:
            # convert tags[] and content[] to strings for SQL
            tags_str = ",".join(note.tags)
            content_str = "\n".join(note.content)

            cursor.execute(
                """
                INSERT INTO notes (name, tags, content) VALUES (?, ?, ?)
                """,
                (note.name, tags_str, content_str),
            )

        conn.commit()
        conn.close()

    def get(self, n=None):
        db_path = os.path.expanduser(self.db)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # return last n rows if specified; otherwise all
        if n:
            cursor.execute("SELECT * FROM notes ORDER BY id DESC LIMIT ?", (n,))
        else:
            cursor.execute("SELECT * FROM notes ORDER BY id DESC")

        rows = cursor.fetchall()

        notes = []
        for row in rows:
            note = Note.from_sql(row)
            notes.append(note)

        notes.reverse()

        return notes


    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, db):
        self._db = db


class Note:
    def __init__(self, name, tags, content, id=None):
        self.id = id
        self.name = name
        self.tags = tags
        self.content = content

    # print like __str__ method for rich's print fn
    def __rich_console__(self, console, options):
        header = f"[b]NOTE #{self.id}[/b]"
        footer = f"[b]END NOTE #{self.id}[/b]"
        tagline = " ".join(f"[b]#[/b]{tag}" for tag in self.tags)
        content = "\n".join(self.content)

        panel = Panel(self.name, title=header, subtitle=tagline)
        yield panel
        md_content = Markdown(content)
        yield md_content
        rule = Rule(title=footer)
        yield rule

    def confirm(self):
        return Confirm.ask("Save note?")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        # set id to placeholder _ for preview
        # only applicable before it is saved to db
        if not id: id = "_"
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        # do not allow for empty names
        # Note.new() method handles default name
        if name:
            self._name = name
        else:
            raise ValueError("Note name cannot be empty")

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        # always sort tags alphabetically
        self._tags = sorted(tags)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @classmethod
    def new(cls, name=None):
        if not name:
            # set a default note name as YYYYMMDD-random_hex
            default = datetime.now().strftime("%Y%m%d-") + "".join(
                random.sample(string.hexdigits, 8)
            )
            name = Prompt.ask("Note name", default=default).strip()
        name = name
        tags = parse_tags(Prompt.ask("Note tags").strip())
        content = eof_input()
        note = Note(name, tags, content)
        return note

    @classmethod
    def from_sql(cls, row):
        tags = row[2].split(",")
        lines = row[3].split("\n")
        note = Note(row[1], tags, lines, id=row[0])
        return note


def main():
    # try here to handle Ctrl-C gracefully
    try:
        args = get_args()
        # initialize NotesDB
        db = NotesDB()
        match args.mode:
            case "new":
                note = Note.new(args.name)
                if note.confirm():
                    db.add([note])

            case "list":
                notes = db.get(args.num)
                for note in notes:
                    print(note, "\n")
            case "search": # TODO: implement better search functionality
                notes = db.get()
                for note in notes:
                    if args.query in note.tags:
                        print(note, "\n")
    except KeyboardInterrupt:
        print()
        sys.exit(0)


def get_args():
    parser = argparse.ArgumentParser(
        prog="cdbr", description="Codebrain programming knowledge db"
    )
    subparsers = parser.add_subparsers(dest="mode")

    new_parser = subparsers.add_parser("new", help="Create a new note")
    new_parser.add_argument(
        "name", nargs="?", default=None, help="name of the new note"
    )

    list_parser = subparsers.add_parser("list", help="List notes")
    list_parser.add_argument(
        "num", nargs="?", default=None, help="last [n] notes to show"
    )

    list_parser = subparsers.add_parser("search", help="List all notes by tag")
    list_parser.add_argument("query", nargs="?", default=None, help="tag to search by")

    args = parser.parse_args()
    return args


def parse_tags(s):
    # split given list of tags by any " #,"
    s = s.strip(" #,")
    tags = re.split(r"[ #,]+", s)
    return tags


# TODO: look into ways to allow user to go back to previous lines
def eof_input():
    # get multiline imput until EOF
    # returned as a list of lines
    panel = Panel(
        "PLEASE ENTER YOUR NOTE BELOW IN MARKDOWN", subtitle="Ctrl-D to Finish"
    )
    print(panel)

    lines = []
    while True:
        try:
            lines.append(input("> "))
        except EOFError:
            print()
            break
    return lines


if __name__ == "__main__":
    main()
