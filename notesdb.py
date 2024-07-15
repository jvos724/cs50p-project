import os
import sqlite3

from note import Note


class NotesDB:
    """Class representing a SQLite DB for a collection of Notes"""
    def __init__(self, db_file: str = ":memory:") -> None:
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Initialize NotesDB SQLite table"""
        if self.db_file != ":memory:":
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        query = """
        CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tags TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add(self, notes: list[Note]) -> None:
        """Save a list of one or more notes to the DB"""
        query = """
        INSERT INTO notes (name, tags, content) VALUES (?, ?, ?)
        """
        for note in notes:
            # convert tags[] and content[] to strings for SQL
            tags_str = ",".join(note.tags)
            content_str = "\n".join(note.content)

            self.cursor.execute(query, (note.name, tags_str, content_str))
            self.conn.commit()

    def get(self, n: int = 0) -> list[Note]:
        """Get all or n=# most recent Notes from DB"""
        query = """
        SELECT * FROM notes ORDER BY id DESC
        """
        # return last n rows if specified; otherwise all
        if n != 0:
            query += "LIMIT ?"
            self.cursor.execute(query, (n,))
        else:
            self.cursor.execute(query)

        rows = self.cursor.fetchall()

        notes = []
        for row in rows:
            note = Note.from_sql(row)
            notes.append(note)

        notes.reverse()

        return notes

    @property
    def db_file(self) -> str:
        return self._db_file

    @db_file.setter
    def db_file(self, f: str) -> None:
        """db_file setter that handles `:memory:` and creates paths"""
        if f == ":memory:":
            self._db_file = f
        else:
            path = os.path.expanduser(f)
            dir = os.path.dirname(path)
            if os.path.exists(dir):
                self._db_file = path
            else:
                os.mkdir(dir)
                self._db_file = path
