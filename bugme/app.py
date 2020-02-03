import sqlite3
from pathlib import Path
from functools import wraps

import db

APP_PATH = '.bugme'


def get_app_instance():
    home = Path.home()
    cwd = Path.cwd()

    while cwd != home:
        path = cwd / APP_PATH
        if path.exists():
            return path
        cwd = cwd.parent

    return None


def require_app_instance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inst = get_app_instance()
        if inst is None:
            raise RuntimeError("No app instance found")
        kwargs.update(instance=inst)
        return func(*args, **kwargs)
    return wrapper


def create_new_instance(path=None):
    if path is None:
        path = Path.cwd()
    path = path / APP_PATH
    path.mkdir()
    db_path = DB_PATH.format(APP_PATH=path)
    create_database_tables(db_path)


def create_new_defect(description, observed, expected, instance):
    record = {"description": description,
              "expected_behaviour": expected,
              "observed_behaviour": observed,
              "status": "OPEN"
              }
    return db.insert_record("bugs", record, instance) 


def update_status(defect_id, status, instance):
    record = {"status": status}
    try:
        db.update_record("bugs", record, "defect_id", defect_id, instance)
    except sqlite3.IntegrityError as invalid_status:
        print("Status value provided is not valid")


def get_status(defect_id, instance):
    defect_id= int(defect_id)
    query = 'SELECT status FROM bugs WHERE defect_id=?;'
    row = (defect_id, )
    return db.run_query(query, row)[0]['status']
        

def get_all_bugs(instance):
    query = 'SELECT * FROM bugs;'
    empty_row = tuple()
    return db.run_query(query, empty_row, instance)


def get_bug(defect_id, instance):
    query = "SELECT * FROM bugs WHERE defect_id=?;"
    row = (defect_id,)
    bug = db.run_query(query, row, instance)[0]

    query = 'SELECT * FROM comments WHERE defect_id=?;'
    row = (defect_id, )
    comments = db.run_query(query, row, instance)
    bug['comments'] = comments
    return bug


def add_comment(defect_id, comment, instance):
    record = {"defect_id": defect_id, "comment": comment }
    return db.insert_record("comments", record, instance)
    

def resolve(defect_id, resolution, instance):
    record = {"resolution": resolution,
              "status": "CLOSED"}
    db.update_record("bugs",record, "defect_id", defect_id, instance)

    query = "UPDATE bugs SET resolution_date=CURRENT_TIMESTAMP WHERE defect_id=?;"
    row = (defect_id, )
    db.run_query(query, row, instance)



def delete_bug(defect_id, instance):
    # added as a hack to remove unwanted tickets.
    # should not be added as functionality
    query = "DELETE FROM bugs WHERE defect_id=?;"
    row = (defect_id, )
    db.run_query(query, row)
