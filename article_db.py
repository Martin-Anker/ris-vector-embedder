
import sqlite3

from torch import Tensor

def init_article_db(db_path: str):
    """
    Initialize the SQLite database.
    Creates required tables if they do not exist.
    Keeps the connection open globally.
    """
    global conn
    conn = sqlite3.connect(db_path)

    create_tables()
    
def create_tables():
    """Create necessary database tables."""

    cur = conn.cursor() 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kurztitel TEXT,
            typ TEXT,
            artikel_anlage TEXT,
            inkrafttretensdatum TEXT,
            index_text TEXT,
            schlagworte TEXT,
            gesetzesnummer TEXT,
            dokumentnummer TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS absatze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            absatz_number TEXT,
            absatz_text TEXT,
            FOREIGN KEY(article_id) REFERENCES articles(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
                absatz_id INTEGER,
                embedding_vector BLOB,
                FOREIGN KEY(absatz_id) REFERENCES absatze(id)
            )
    """)

    conn.commit()

def save_article(article_data: dict, absatze: list[tuple[str, str]]):
    """Save article data into the database."""
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO articles (
            kurztitel, typ, artikel_anlage, inkrafttretensdatum,
            index_text, schlagworte, gesetzesnummer, dokumentnummer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article_data.get('Kurztitel'),
        article_data.get('Typ'),
        article_data.get('Paragraph_Artikel_Anlage'),
        article_data.get('Inkrafttretensdatum'),
        article_data.get('Index'),
        article_data.get('Schlagworte'),
        article_data.get('Gesetzesnummer'),
        article_data.get('Dokumentnummer')
    ))

    article_id = cur.lastrowid
    print(absatze)
    for absatz_number, absatz_text in absatze:
        cur.execute("""
            INSERT INTO absatze (article_id, absatz_number, absatz_text)
            VALUES (?, ?, ?)
        """, (article_id, absatz_number, absatz_text))

    conn.commit()

def load_formatted_absatz(absatz_id: int) -> str:
    """Load and format Absatz text by its ID with metadata from the article."""
    cur = conn.cursor()
    cur.execute("""
        SELECT a.kurztitel, a.typ, a.artikel_anlage, a.schlagworte,
               ab.absatz_number, ab.absatz_text
        FROM absatze ab
        JOIN articles a ON ab.article_id = a.id
        WHERE ab.id = ?
    """, (absatz_id,))
    row = cur.fetchone()
    if row:
        kurztitel, typ, artikel_anlage, schlagworte, absatz_number, absatz_text = row
        formatted_text = (
            f"Kurztitel: {kurztitel}\n"
            f"Typ: {typ}\n"
            f"§/Artikel/Anlage: {artikel_anlage}\n"
            f"Schlagworte: {schlagworte}\n"
            f"Absatz {absatz_number}: {absatz_text}"
        )
        return formatted_text
    return ""

def save_embedding(absatz_id: int, embedding_vector: Tensor):
    """Save embedding vector for a given Absatz."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO embeddings (absatz_id, embedding_vector)
        VALUES (?, ?)
    """, (absatz_id, embedding_vector))
    conn.commit()

def load_all_embeddings():
    """Load all embeddings from the database."""
    cur = conn.cursor()
    cur.execute("SELECT absatz_id, embedding_vector FROM embeddings")
    return cur.fetchall()

def load_all_absatze():
    """Load all Absatz IDs and texts from the database."""
    cur = conn.cursor()
    cur.execute("SELECT id, absatz_text FROM absatze")
    return cur.fetchall()