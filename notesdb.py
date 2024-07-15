import os
import sqlite3

from note import Note

# default db file if none is specified
# TODO: add support for Windows path here
DB_FILE = "~/.local/share/cb/notes.db"


class NotesDB:
    def __init__(self, db_file=DB_FILE):
        self.db_file = os.path.expanduser(db_file)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
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

    def add(self, notes):
        query = """
        INSERT INTO notes (name, tags, content) VALUES (?, ?, ?)
        """
        for note in notes:
            # convert tags[] and content[] to strings for SQL
            tags_str = ",".join(note.tags)
            content_str = "\n".join(note.content)

            self.cursor.execute(query, (note.name, tags_str, content_str))
            self.conn.commit()

    def get(self, n=None):
        query = """
        SELECT * FROM notes ORDER BY id DESC
        """
        # return last n rows if specified; otherwise all
        if n:
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
    def db(self):
        return self._db

    @db.setter
    def db(self, db):
        self._db = db
