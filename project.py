#!/home/jeff/Dev/cs50p/project/.venv/bin/python
import argparse
import re
import sys

from rich import print
from rich.panel import Panel

from note import Note
from notesdb import NotesDB


def main():
    # try here to handle Ctrl-C gracefully
    try:
        args = get_args()
        # initialize NotesDB
        db = NotesDB()
        match args.mode:
            case "new" | "n":
                note = Note.new(args.name)
                if note.confirm():
                    db.add([note])

            case "list" | "l":
                notes = db.get(args.num)
                for note in notes:
                    print(note, "\n")
            case "search" | "s":  # TODO: implement better search functionality
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

    new_parser = subparsers.add_parser("new", aliases=["n"], help="Create a new note")
    new_parser.add_argument(
        "name", nargs="?", default=None, help="name of the new note"
    )

    list_parser = subparsers.add_parser("list", aliases=["l"], help="List notes")
    list_parser.add_argument(
        "num", nargs="?", default=None, help="last [n] notes to show"
    )

    list_parser = subparsers.add_parser(
        "search", aliases=["s"], help="List all notes by tag"
    )
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
