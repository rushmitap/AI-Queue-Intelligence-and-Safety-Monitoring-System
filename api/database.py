import sqlite3
import json
import time

DATABASE_PATH = "data/db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            count INTEGER,
            risk_score Real,
            risk_level TEXT,
            growth INTEGER,
            alerts TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_stat(stat_dict):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    alerts_json = json.dumps(stat_dict.get("alerts", []))
    c.execute('''
        INSERT INTO stats (timestamp, count, risk_score, risk_level, growth, alerts)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        time.time(),
        stat_dict.get("count", 0),
        stat_dict.get("risk_score", 0),
        stat_dict.get("risk_level", "LOW"),
        stat_dict.get("growth", 0),
        alerts_json
    ))
    conn.commit()
    conn.close()

def get_recent_stats(limit=50):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM stats ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    
    # Return chronologically (oldest to newest for plotting)
    return [dict(r) for r in reversed(rows)]
