import bugme.db as db
import pytest


def test_get_connection():
    app_instance = "bugme/.bugme"
    con = db.get_connection(app_instance)
    query = "SELECT name FROM sqlite_master where type='table';"
    rows = con.execute(query).fetchall()
    assert len(rows) == 3, rows # 2 tables 1 sequence table
    

