"""Banco central SQLite. Apenas o processo servidor abre o arquivo de dados."""
from __future__ import annotations
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 1
SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL COLLATE NOCASE UNIQUE,
 display_name TEXT NOT NULL, password_hash TEXT, role TEXT NOT NULL DEFAULT 'operator'
 CHECK(role IN ('admin','operator','viewer')),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS themes (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL COLLATE NOCASE UNIQUE,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS subthemes (
 id INTEGER PRIMARY KEY, theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE RESTRICT,
 name TEXT NOT NULL COLLATE NOCASE,
 UNIQUE(theme_id,name)
);
CREATE TABLE IF NOT EXISTS storage_units (
 id INTEGER PRIMARY KEY, stable_id TEXT NOT NULL UNIQUE, label TEXT NOT NULL,
 root_path TEXT NOT NULL, available INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0,1)),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS artworks (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL,
 theme_id INTEGER REFERENCES themes(id) ON DELETE RESTRICT,
 subtheme_id INTEGER REFERENCES subthemes(id) ON DELETE RESTRICT,
 keywords TEXT NOT NULL DEFAULT '', created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
 revision INTEGER NOT NULL DEFAULT 1 CHECK(revision >= 1),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS artwork_files (
 id INTEGER PRIMARY KEY, artwork_id INTEGER NOT NULL REFERENCES artworks(id) ON DELETE RESTRICT,
 storage_id INTEGER NOT NULL REFERENCES storage_units(id) ON DELETE RESTRICT,
 relative_path TEXT NOT NULL, sha256 TEXT CHECK(sha256 IS NULL OR length(sha256)=64),
 size_bytes INTEGER CHECK(size_bytes IS NULL OR size_bytes>=0),
 status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available','missing','trash')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(storage_id,relative_path)
);
CREATE TABLE IF NOT EXISTS file_operations (
 id INTEGER PRIMARY KEY, operation_key TEXT NOT NULL UNIQUE,
 operation_type TEXT NOT NULL CHECK(operation_type IN ('copy','move','rename','delete','restore')),
 state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','running','completed','failed','cancelled')),
 source_path TEXT, destination_path TEXT,
 requested_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS audit_events (
 id INTEGER PRIMARY KEY, actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
 action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id INTEGER,
 details TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_artworks_title ON artworks(title COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_artworks_theme ON artworks(theme_id,subtheme_id);
CREATE INDEX IF NOT EXISTS idx_files_artwork ON artwork_files(artwork_id);
CREATE INDEX IF NOT EXISTS idx_files_sha ON artwork_files(sha256);
CREATE INDEX IF NOT EXISTS idx_operations_state ON file_operations(state);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
"""

class Database:
 def __init__(self, path: str | Path):
  self.path = Path(path).expanduser().resolve()
  self._init_lock = threading.Lock()

 def connect(self) -> sqlite3.Connection:
  con = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
  con.row_factory = sqlite3.Row
  con.execute('PRAGMA foreign_keys=ON')
  con.execute('PRAGMA busy_timeout=10000')
  con.execute('PRAGMA journal_mode=WAL')
  return con

 def initialize(self) -> None:
  with self._init_lock:
   self.path.parent.mkdir(parents=True,exist_ok=True)
   with self.connect() as con:
    con.executescript(SCHEMA)
    current = con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
    if current is None:
     con.execute("INSERT INTO schema_meta(key,value) VALUES('schema_version',?)",(str(SCHEMA_VERSION),))
    elif int(current['value']) != SCHEMA_VERSION:
     raise RuntimeError(f'Versão de banco incompatível: {current["value"]}')
    integrity = con.execute('PRAGMA quick_check').fetchone()[0]
    if integrity != 'ok': raise RuntimeError(f'Falha de integridade SQLite: {integrity}')

 @contextmanager
 def transaction(self):
  con=self.connect()
  try:
   con.execute('BEGIN IMMEDIATE')
   yield con
   con.execute('COMMIT')
  except BaseException:
   if con.in_transaction: con.execute('ROLLBACK')
   raise
  finally: con.close()

 def stats(self) -> dict[str,int]:
  with self.connect() as con:
   return {table:con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in ('users','themes','subthemes','storage_units','artworks','artwork_files')}

 def create_theme(self,name:str)->int:
  name=' '.join(name.split())
  if not name or len(name)>120: raise ValueError('Nome do tema inválido')
  with self.transaction() as con:
   cursor=con.execute('INSERT INTO themes(name) VALUES(?)',(name,))
   return int(cursor.lastrowid)

 def create_artwork(self,title:str,theme_id:int|None=None,subtheme_id:int|None=None,keywords:str='')->int:
  title=' '.join(title.split())
  if not title or len(title)>255: raise ValueError('Título inválido')
  with self.transaction() as con:
   if subtheme_id is not None:
    sub=con.execute('SELECT theme_id FROM subthemes WHERE id=?',(subtheme_id,)).fetchone()
    if sub is None or theme_id != sub['theme_id']: raise ValueError('Subtema não pertence ao tema')
   cursor=con.execute('INSERT INTO artworks(title,theme_id,subtheme_id,keywords) VALUES(?,?,?,?)',(title,theme_id,subtheme_id,keywords))
   return int(cursor.lastrowid)

 def update_artwork(self,artwork_id:int,revision:int,title:str)->bool:
  title=' '.join(title.split())
  if not title or len(title)>255: raise ValueError('Título inválido')
  with self.transaction() as con:
   cur=con.execute("UPDATE artworks SET title=?,revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE id=? AND revision=?",(title,artwork_id,revision))
   return cur.rowcount==1
