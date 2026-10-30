"""Etapa 04: estatísticas reais e integridade da API."""
from fastapi.testclient import TestClient
from app.server.application import create_app
from app.server.database import Database


def test_dashboard_empty(tmp_path):
    db = Database(tmp_path / 'test.sqlite3')
    with TestClient(create_app(db)) as client:
        response = client.get('/dashboard/stats')
    assert response.status_code == 200
    assert response.json() == {'artworks': 0, 'themes': 0, 'storage_units': 0, 'recent_operations': 0}


def test_dashboard_real_counts(tmp_path):
    db = Database(tmp_path / 'test.sqlite3')
    with TestClient(create_app(db)) as client:
        db.create_theme('Infantil')
        db.create_artwork('Arte de teste')
        with db.transaction() as con:
            con.execute("INSERT INTO storage_units(stable_id,label,root_path,available) VALUES('disk1','HD 1','D:/',1)")
            con.execute("INSERT INTO storage_units(stable_id,label,root_path,available) VALUES('disk2','HD 2','E:/',0)")
            con.execute("INSERT INTO file_operations(operation_key,operation_type,state,created_at) VALUES('op1','copy','completed',CURRENT_TIMESTAMP)")
            con.execute("INSERT INTO file_operations(operation_key,operation_type,state,created_at) VALUES('op2','move','completed',datetime('now','-9 days'))")
        response = client.get('/dashboard/stats')
    assert response.status_code == 200
    assert response.json() == {'artworks': 1, 'themes': 1, 'storage_units': 1, 'recent_operations': 1}
