#!/home/jeff/Dev/cs50p/project/.venv/bin/python
import argparse
import re
import sys

from rich import print
from rich.panel import Panel

from note import Note
from notesdb import NotesDB


DEFAULT_DB = "~/.local/share/cb/notes.db"  # TODO: Windows support


def main() -> None:
    """Main function call for SC that handles Ctrl-C exits"""

    args = get_args()
    db = NotesDB(DEFAULT_DB)
    try:
        match args.mode:
            case "new" | "n":
                note = Note.new(args.name)
                if note.confirm():
                    db.add([note])
            case "list" | "l":
                notes = db.get(args.num)
                if notes:
                    for note in notes:
                        print(note, "\n")
                else:
                    sys.exit("No notes found.")
            case "search" | "s":
                try:
                    notes = db.search(args.query)
                except ValueError:
                    sys.exit("Search term required.")
                else:
                    if notes:
                        for note in notes:
                            print(note, "\n")
                    else:
                        sys.exit("No matches found.")
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    finally:
        db.close()


def get_args() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        argparse.Namespace: The parsed arguments
    """

    parser = argparse.ArgumentParser(
        prog="cdbr", description="Codebrain programming knowledge db"
    )
    subparsers = parser.add_subparsers(dest="mode")

    new_parser = subparsers.add_parser("new", aliases=["n"], help="Create a new note")
    new_parser.add_argument(
        "name", nargs="?", default=None, help="name of the new note"
    )

    list_parser = subparsers.add_parser("list", aliases=["l"], help="List notes")
    list_parser.add_argument("num", nargs="?", default=0, help="last [n] notes to show")

    list_parser = subparsers.add_parser(
        "search", aliases=["s"], help="List all notes by tag"
    )
    list_parser.add_argument("query", nargs="?", default=None, help="tag to search by")

    return parser.parse_args()


def parse_tags(s: str) -> list[str]:
    """Split a given list of tags by any " #," characters

    Args:
        s (str): The string containing tags

    Returns:
        list[str]: A list of parsed tags
    """

    s = s.strip(" #,")
    return re.split(r"[ #,]+", s)


# TODO: look into ways to allow user to go back to previous lines
def eof_input() -> list[str]:
    """Get multiline input until EOF, returned as a list of lines

    Returns:
        list[str]: A list of lines entered by the user
    """

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
