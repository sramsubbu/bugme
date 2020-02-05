"""
core functions and logic that runs the app
"""
import sqlite3
from pathlib import Path
from functools import wraps

import db

APP_PATH = '.bugme'


def get_app_instance():
    """ return the instance of the app that contains the bugme files """
    home = Path.home()
    cwd = Path.cwd()

    while cwd != home:
        path = cwd / APP_PATH
        if path.exists():
            return path
        cwd = cwd.parent

    return None


def require_app_instance(func):
    """ decorator that implicitly passes the app instance variable to the wrapped function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inst = get_app_instance()
        if inst is None:
            raise RuntimeError("No app instance found")
        kwargs.update(instance=inst)
        return func(*args, **kwargs)
    return wrapper


def create_new_instance(path=None):
    """ create a new instance in the current directory """
    if path is None:
        path = Path.cwd()
    path = path / APP_PATH
    path.mkdir()
    db.create_database_tables(path)


def create_new_defect(description, observed, expected, instance):
    """ log a new defect into the database """
    record = {"description": description,
              "expected_behaviour": expected,
              "observed_behaviour": observed,
              "status": "OPEN"
              }
    return db.insert_record("bugs", record, instance)


def update_status(defect_id, status, instance):
    """ update the status of a defect """
    record = {"status": status}
    try:
        db.update_record("bugs", record, "defect_id", defect_id, instance)
    except sqlite3.IntegrityError:
        print("Status value provided is not valid")


def get_status(defect_id, instance):
    """ get the status of the given defect """
    defect_id = int(defect_id)
    query = 'SELECT status FROM bugs WHERE defect_id=?;'
    row = (defect_id, )
    return db.run_query(query, row, instance)[0]['status']


def get_all_bugs(instance):
    """ get all existing bugs from the database """
    query = 'SELECT * FROM bugs;'
    empty_row = tuple()
    return db.run_query(query, empty_row, instance)


def get_bug(defect_id, instance):
    """ get a particular bug from database """
    query = "SELECT * FROM bugs WHERE defect_id=?;"
    row = (defect_id,)
    bug = db.run_query(query, row, instance)[0]

    query = 'SELECT * FROM comments WHERE defect_id=?;'
    row = (defect_id, )
    comments = db.run_query(query, row, instance)
    bug['comments'] = comments
    return bug


def add_comment(defect_id, comment, instance):
    """ add a comment to the database """
    record = {"defect_id": defect_id, "comment": comment}
    return db.insert_record("comments", record, instance)


def resolve(defect_id, resolution, instance):
    """ close the bug with resolution """
    record = {"resolution": resolution,
              "status": "CLOSED"}
    db.update_record("bugs", record, "defect_id", defect_id, instance)

    query = "UPDATE bugs SET resolution_date=CURRENT_TIMESTAMP WHERE defect_id=?;"
    row = (defect_id, )
    db.run_query(query, row, instance)



def delete_bug(defect_id, instance):
    # added as a hack to remove unwanted tickets.
   # should not be added as functionality
    query = "DELETE FROM bugs WHERE defect_id=?;"
    row = (defect_id, )
    db.run_query(query, row, instance)
