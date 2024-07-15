import random
import string
from datetime import datetime

from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule


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
        if not id:
            id = "_"
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
        from project import eof_input, parse_tags

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
