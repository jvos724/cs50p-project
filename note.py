import string
import random
from datetime import datetime

from typing import Generator, List, Optional, TYPE_CHECKING
from rich.console import Console, ConsoleOptions, RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule


class Note:
    """
    Class representing a note, containing an id, name, tags, and content.

    Attributes:
        id (int): The identifier of the note
        name (str): The name/title of the note
        tags (List[str]): A list of tags associated with the note
        content (List[str]): The content of the note, one line per string
    """

    def __init__(
        self, name: str, tags: list[str], content: list[str], id: int = 0
    ) -> None:
        self.id = id
        self.name = name
        self.tags = tags
        self.content = content

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Generator["RenderableType", None, None]:
        """
        Print function to display the note using rich

        Yields:
            RenderableType: Rich renderable objects
        """

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

    def confirm(self) -> bool:
        """
        Asks for confirmation to save the note.

        Returns:
            bool: True to save the note, false otherwise
        """

        return Confirm.ask("Save note?")

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        """
        Sets the id attribute. If id is not provided, default to 0.
        Typically id is retrieved from the SQLite DB whenever retrieved,
        so '0' is just a placeholder while the note is only in memory.

        Args:
            id (int): The id of the note
        """

        if not id:
            id = 0
        self._id = id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets the name attribute.

        Args:
            name (str): The name of the note
        Raises:
            ValueError: If the name is empty
        """

        if name:
            self._name = name
        else:
            raise ValueError("Note name cannot be empty")

    @property
    def tags(self) -> List[str]:
        return self._tags

    @tags.setter
    def tags(self, tags: List[str]) -> None:
        """
        Sets the tags attribute. Sorts the tags alphabetically.

        Args:
            tags (List[str]): A list of tags
        """

        self._tags = sorted(tags)

    @property
    def content(self) -> List[str]:
        return self._content

    @content.setter
    def content(self, content: List[str]) -> None:
        """
        Sets the content attribute.

        Args:
            content (List[str]): The content of the note as a list of lines
        """

        self._content = content

    @classmethod
    def new(cls, name: Optional[str] = None) -> "Note":
        """
        Creates a new note by prompting the user for input.

        Args:
            name (Optional[str]): Name for the note. If not provided, a default name is generated

        Returns:
            Note: A new instance of the note class
        """

        from project import eof_input, parse_tags

        if not name:
            default = datetime.now().strftime("%Y%m%d-") + "".join(
                random.sample(string.hexdigits, 8)
            )
            name = Prompt.ask("Note name", default=default).strip()
        tags = parse_tags(Prompt.ask("Note tags").strip())
        content = eof_input()
        return cls(name, tags, content)

    @classmethod
    def from_sql(cls, row: tuple) -> "Note":
        tags = row[2].split(",")
        lines = row[3].split("\n")
        return cls(row[1], tags, lines, id=row[0])
