"""Testes de esquema, transações, integridade, concorrência e integração."""
import sqlite3
import pytest
import httpx
from fastapi.testclient import TestClient
from app.server.database import Database,SCHEMA_VERSION
from app.server.application import create_app

@pytest.fixture
def db(tmp_path):
    database=Database(tmp_path/'dados'/'catalogo.sqlite3')
    database.initialize()
    return database

def test_initialization_and_reopen(db):
    db.initialize()
    assert db.path.exists()
    assert db.stats()['artworks']==0
    with db.connect() as con:
        assert con.execute('PRAGMA foreign_keys').fetchone()[0]==1
        assert con.execute('PRAGMA journal_mode').fetchone()[0]=='wal'
        assert con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0]==str(SCHEMA_VERSION)

def test_tables(db):
    with db.connect() as con:
        tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {'users','themes','subthemes','storage_units','artworks','artwork_files','file_operations','audit_events','schema_meta'}<=tables

def test_theme_and_artwork(db):
    theme=db.create_theme('  Infantil  ')
    artwork=db.create_artwork('  Arte   floral ',theme)
    with db.connect() as con:
        assert con.execute('SELECT title FROM artworks WHERE id=?',(artwork,)).fetchone()[0]=='Arte floral'
        with pytest.raises(sqlite3.IntegrityError): con.execute('INSERT INTO themes(name) VALUES(?)',('infantil',))

def test_foreign_keys(db):
    with db.transaction() as con:
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('INSERT INTO subthemes(theme_id,name) VALUES(999,?)',('Flores',))

def test_rollback(db):
    with pytest.raises(RuntimeError):
        with db.transaction() as con:
            con.execute('INSERT INTO themes(name) VALUES(?)',('Teste',))
            raise RuntimeError('interrupção')
    assert db.stats()['themes']==0

def test_revision_conflict(db):
    artwork=db.create_artwork('Original')
    assert db.update_artwork(artwork,1,'Alterada')
    assert not db.update_artwork(artwork,1,'Conflito')
    with db.connect() as con:
        row=con.execute('SELECT title,revision FROM artworks WHERE id=?',(artwork,)).fetchone()
    assert (row['title'],row['revision'])==('Alterada',2)

def test_subtheme_must_match_theme(db):
    a=db.create_theme('A'); b=db.create_theme('B')
    with db.transaction() as con:
        sub=con.execute('INSERT INTO subthemes(theme_id,name) VALUES(?,?)',(a,'X')).lastrowid
    with pytest.raises(ValueError): db.create_artwork('Invalida',b,sub)

def test_idempotent_operation_key(db):
    with db.transaction() as con:
        con.execute("INSERT INTO file_operations(operation_key,operation_type) VALUES('req1','copy')")
    with pytest.raises(sqlite3.IntegrityError):
        with db.transaction() as con:
            con.execute("INSERT INTO file_operations(operation_key,operation_type) VALUES('req1','copy')")

def test_api_lifespan_and_private_database(db):
    with TestClient(create_app(db)) as client:
        assert client.get('/health').status_code==200
        assert client.get('/info').json()['schema_version']==SCHEMA_VERSION
        assert client.get('/artworks').status_code==404
        assert client.get('/database').status_code==404
    assert db.path.exists()

def test_invalid_values(db):
    with pytest.raises(ValueError): db.create_theme('  ')
    with pytest.raises(ValueError): db.create_artwork('  ')

def test_sqlite_integrity(db):
    with db.connect() as con:
        assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
