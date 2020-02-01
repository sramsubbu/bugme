import sqlite3
from pathlib import Path
from functools import wraps

APP_PATH = '.bugme'
DB_PATH = '{APP_PATH}/bugs.db'

def get_connection(db_path):
    con = sqlite3.connect(db_path, isolation_level=None)

    def dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    con.row_factory = dict_factory
    return con

def create_database_tables(db_path):
    con = get_connection(db_path)
    with open("ddl.sql") as fp:
        sql_script = fp.read()

    con.executescript(sql_script)

def generate_update_query(tablename, record_dict, pk_name, pk_value):
    query_template = 'UPDATE {table} SET {update_string} WHERE {pk_name}=?;'
    update_string = ','.join('{name}=?'.format(name=name) for name in record_dict)
    row = tuple(record_dict.values()) + (pk_value, )
    query = query_template.format(table=tablename,
                                  update_string=update_string,
                                  pk_name=pk_name)
    return query, row


def generate_insert_query(tablename, record_dict):
    query_template = 'INSERT INTO {table}({names}) VALUES({values});'
    names = ','.join(record_dict.keys())
    values = ','.join('?' for _ in record_dict)
    row = tuple(record_dict.values())
    query = query_template.format(table=tablename, names=names, values=values)
    return query, row


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
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)
    record = {"description": description,
              "expected_behaviour": expected,
              "observed_behaviour": observed,
              "status" : "OPEN"}
    query, row = generate_insert_query("bugs", record)
    res = dbcon.execute(query, row)
    return res.lastrowid

def update_status(defect_id, status, instance):
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)
    record = {"status": status}
    query, row = generate_update_query("bugs", record, "defect_id", defect_id)
    try:
        dbcon.execute(query, row)
    except sqlite3.IntegrityError as e:
        print("Invalid status value provided")

        
def get_status(defect_id, instance):
    defect_id = int(defect_id)
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)
    query = "SELECT status FROM bugs WHERE defect_id=?;"
    row = (defect_id, )
    res = dbcon.execute(query, row).fetchall()
    return res[0]['status']
    
    
    
def get_all_bugs(instance):
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)
    query = 'SELECT * FROM bugs;'
    bugs = dbcon.execute(query).fetchall()
    return bugs


def get_bug(defect_id, instance):
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)
    query = 'SELECT * FROM bugs WHERE defect_id=?;'
    row = (defect_id, )
    bug = dbcon.execute(query, row).fetchall()
    bug = bug[0]

    comments = 'SELECT * FROM comments WHERE defect_id=?;'
    row = (defect_id, )
    comments = dbcon.execute(comments, row).fetchall()
    bug['comments'] = comments
    return bug


def add_comment(defect_id, comment, instance):
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)

    record = {"defect_id": defect_id, "comment": comment}
    query, row = generate_insert_query("comments", record)
    cid = dbcon.execute(query, row)
    return cid
    

def resolve(defect_id, resolution, instance):
    db_path = DB_PATH.format(APP_PATH=instance)
    dbcon = get_connection(db_path)

    record = {"resolution": resolution,  "status": "CLOSED"}
    query, row = generate_update_query("bugs", record, "defect_id", defect_id)
    dbcon.execute(query, row)

    query = 'UPDATE bugs SET resolution_date=CURRENT_TIMESTAMP WHERE defect_id=?;'
    row = (defect_id, )
    dbcon.execute(query, row)
