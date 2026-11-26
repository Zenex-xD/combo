# language: Python 3.11 — db.py
import aiosqlite
import time
from config import DB_PATH

_conn: aiosqlite.Connection | None = None


async def init_db():
    global _conn
    _conn = await aiosqlite.connect(DB_PATH)
    await _conn.execute("""
        CREATE TABLE IF NOT EXISTS hits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            email TEXT NOT NULL,
            pw TEXT NOT NULL,
            status TEXT NOT NULL,
            detail TEXT,
            ts INTEGER NOT NULL
        )
    """)
    await _conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_hits_service_ts ON hits(service, ts)"
    )
    await _conn.commit()
    return _conn


async def store_hit(service, email, pw, status, detail):
    await _conn.execute(
        "INSERT INTO hits(service, email, pw, status, detail, ts) VALUES (?, ?, ?, ?, ?, ?)",
        (service, email, pw, status, detail or "", int(time.time())),
    )
    await _conn.commit()


async def count_hits(service=None, status=None, since=0):
    q = "SELECT COUNT(*) FROM hits WHERE ts >= ?"
    args = [since]
    if service:
        q += " AND service = ?"
        args.append(service)
    if status:
        q += " AND status = ?"
        args.append(status)
    cur = await _conn.execute(q, args)
    row = await cur.fetchone()
    return row[0]


async def fetch_hits(service, since=0, limit=200):
    cur = await _conn.execute(
        "SELECT email, pw, status, detail FROM hits "
        "WHERE service = ? AND ts >= ? AND status IN ('HIT', '2FA', 'LOCKED') "
        "ORDER BY id DESC LIMIT ?",
        (service, since, limit),
    )
    return await cur.fetchall()


async def close_db():
    global _conn
    if _conn is not None:
        await _conn.close()
        _conn = None
