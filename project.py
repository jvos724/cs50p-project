#!/home/jeff/Dev/cs50p/project/.venv/bin/python
import argparse
import os
import random
import re
import sqlite3
import string
import sys
from datetime import datetime

# NOTE: commented out unused imports
from rich import print

# from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

# from rich.table import Table


DB_FILE = "~/.local/share/cb/notes.db"


class Note:
    def __init__(self, name="", tags=[], content=[]):
        self.name = name
        self.tags = tags
        self.content = content

    # print method for rich's print fn
    def __rich_console__(self, console, options):
        header = f"[b]Note:[/b] {self.name}"
        tagline = " ".join(f"[b]#[/b]{tag}" for tag in self.tags)
        panel = Panel(header, subtitle=tagline)
        yield panel
        content = "\n".join(self.content)
        md_content = Markdown(content)
        yield md_content

    def confirm(self):
        return Confirm.ask("Save note?")

    # default save to DB_FILE const
    def save(self, db=DB_FILE):
        db_path = os.path.expanduser(db)
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

        tags_str = ",".join(self.tags)
        content_str = "\n".join(self.content)

        cursor.execute(
            """
        INSERT INTO notes (name, tags, content) VALUES (?, ?, ?)
        """,
            (self.name, tags_str, content_str),
        )

        conn.commit()
        conn.close()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        self._tags = sorted(tags)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @classmethod
    def new(cls, name=None):
        note = Note()
        if not name:
            default = datetime.now().strftime("%Y%m%d-") + "".join(
                random.sample(string.hexdigits, 8)
            )
            name = Prompt.ask("Note name", default=default).strip()
        note.name = name
        note.tags = parse_tags(Prompt.ask("Note tags").strip())
        note.content = eof_input()
        return note

    @classmethod
    def get_all(cls, search, db=DB_FILE):
        db_path = os.path.expanduser(db)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes")
        rows = cursor.fetchall()

        conn.close()

        notes = []
        for row in rows:
            tags = row[2].split(",")
            lines = row[3].split("\n")
            note = Note(row[1], tags, lines)
            notes.append(note)

        # if `cb list all`, return all notes
        # else return n=last n notes
        if search == "all" or search == None:
            return notes
        else:
            try:
                n = int(search) * -1
                return notes[n:]
            except ValueError:
                sys.exit("Invalid number of notes")


def main():
    # try here to handle Ctrl-C gracefully
    try:
        args = get_args()
        match args.mode:
            case "new":
                note = Note.new(args.name)
                if note.confirm():
                    note.save()

            case "list":
                notes = Note.get_all(args.num)
                for i, note in enumerate(notes):
                    print(note)
                    if i == len(notes) - 1:
                        break
                    else:
                        print("\n")
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
        "name", nargs="?", default=None, help="Name of the new note"
    )

    list_parser = subparsers.add_parser("list", help="List notes")
    list_parser.add_argument("num", nargs="?", default=None, help="Show last [n] notes")

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
