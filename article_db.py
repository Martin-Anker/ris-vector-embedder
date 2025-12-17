
import sqlite3

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
    for absatz_number, absatz_text in absatze:
        cur.execute("""
            INSERT INTO absatze (article_id, absatz_number, absatz_text)
            VALUES (?, ?, ?)
        """, (article_id, absatz_number, absatz_text))

    conn.commit()
