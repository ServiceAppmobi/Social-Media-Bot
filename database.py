import sqlite3
import datetime
from config import DB_PATH

def init_db():
    """Tworzy strukturę tabeli, jeśli baza jeszcze nie istnieje."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            post_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            country TEXT DEFAULT 'BR',
            source_channel TEXT NOT NULL,
            title TEXT,
            url TEXT,
            author TEXT,
            content_snippet TEXT,
            lead_type TEXT,
            ai_draft TEXT,
            notified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Bezpieczna migracja kolumny country jeśli tabela już istniała wcześniej
    cursor.execute("PRAGMA table_info(leads)")
    columns = [col[1] for col in cursor.fetchall()]
    if "country" not in columns:
        cursor.execute("ALTER TABLE leads ADD COLUMN country TEXT DEFAULT 'BR'")
    
    conn.commit()
    conn.close()

def is_post_seen(post_id: str) -> bool:
    """Sprawdza, czy wpis był już wcześniej pobrany i przetworzony."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM leads WHERE post_id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_lead(post_id: str, platform: str, source_channel: str, title: str, 
              url: str, author: str, content_snippet: str, lead_type: str, 
              ai_draft: str, country: str = "BR", notified: int = 0):
    """Zapisuje nowy lead do bazy danych."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO leads 
        (post_id, platform, country, source_channel, title, url, author, content_snippet, lead_type, ai_draft, notified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (post_id, platform, country, source_channel, title, url, author, content_snippet, lead_type, ai_draft, notified))
    conn.commit()
    conn.close()

def mark_notified(post_id: str):
    """Oznacza lead jako wysłany w powiadomieniu."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET notified = 1 WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_stats():
    """Zwraca statystyki z podziałem na kraje i kategorie."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE country = 'BR'")
    brazil_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE country = 'MX'")
    mexico_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'SERVICE_SEEKER'")
    service_seekers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'WORK_SEEKER'")
    work_seekers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE notified = 1")
    notified = cursor.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "brazil": brazil_count,
        "mexico": mexico_count,
        "service_seekers": service_seekers,
        "work_seekers": work_seekers,
        "notified": notified
    }
