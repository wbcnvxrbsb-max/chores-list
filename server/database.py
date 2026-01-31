import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'chores.db'
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'


def get_db():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with schema if needed."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_db()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.close()
    # Run migrations for existing databases
    migrate_db()


def migrate_db():
    """Run database migrations for schema updates."""
    conn = get_db()

    # Check if frequency column exists in chores table
    cursor = conn.execute("PRAGMA table_info(chores)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'frequency' not in columns:
        # Add frequency column with default 'daily' for existing chores
        conn.execute("ALTER TABLE chores ADD COLUMN frequency TEXT DEFAULT 'daily'")
        conn.commit()

    conn.close()


def query_db(query, args=(), one=False):
    """Execute a query and return results."""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute a query and return lastrowid."""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    lastrowid = cur.lastrowid
    conn.close()
    return lastrowid
