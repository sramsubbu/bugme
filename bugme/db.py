"""
database related functions to handle CRUD operations of the database. Also has utilities to setup
the database
"""

import sqlite3

DB_PATH = '{app_path}/bugs.db'

def get_connection(app_instance):
    """ get the connection to the database with the prefered parameters"""
    db_path = DB_PATH.format(app_path=app_instance)
    con = sqlite3.connect(db_path, isolation_level=None)

    def dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    con.row_factory = dict_factory
    return con

def create_database_tables(app_instance):
    """ Create the database tables when initialising a bugme instance """
    con = get_connection(app_instance)
    with open("ddl.sql") as script_file:
        sql_script = script_file.read()

    con.executescript(sql_script)

def generate_update_query(tablename, record_dict, pk_name, pk_value):
    """ generate update query """
    query_template = 'UPDATE {table} SET {update_string} WHERE {pk_name}=?;'
    update_string = ','.join('{name}=?'.format(name=name) for name in record_dict)
    row = tuple(record_dict.values()) + (pk_value, )
    query = query_template.format(table=tablename,
                                  update_string=update_string,
                                  pk_name=pk_name)
    return query, row


def generate_insert_query(tablename, record_dict):
    """ generate the insert query """
    query_template = 'INSERT INTO {table}({names}) VALUES({values});'
    names = ','.join(record_dict.keys())
    values = ','.join('?' for _ in record_dict)
    row = tuple(record_dict.values())
    query = query_template.format(table=tablename, names=names, values=values)
    return query, row

def insert_record(tablename, record_dict, app_instance):
    """ insert the given record into the database table 'tablename' """
    dbcon = get_connection(app_instance)
    query, row = generate_insert_query(tablename, record_dict)
    res = dbcon.execute(query, row)
    return res.lastrowid


def update_record(tablename, record_dict, pk_name, pk_value, app_instance):
    """ update the record with primary key 'pk_value' with the record_dict """
    dbcon = get_connection(app_instance)
    query, row = generate_update_query(tablename, record_dict, pk_name, pk_value)
    dbcon.execute(query, row)


def run_query(sql_query, record_tuple, app_instance):
    """ run the given sql query with the record_tuple and return the result """
    dbcon = get_connection(app_instance)
    res = dbcon.execute(sql_query, record_tuple).fetchall()
    return res

