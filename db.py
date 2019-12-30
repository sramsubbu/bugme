import sqlite3

from app_config import DB_PATH 


def generate_insert_query(table_name, record_dict):
    query_template = 'INSERT INTO {table}({names}) VALUES({values});'
    names = ','.join(record_dict.keys())
    values = ','.join('?' for _ in record_dict)

    row = tuple(record_dict.values())
    query = query_template.format(table=table_name,
                                  names=names,
                                  values=values)
    return query, row


def get_connection(db_path=DB_PATH):
    con = sqlite3.connect(db_path)

    def dict_factory(cursor, row):
        return {col[0]:row[idx] for idx, col in enumerate(cursor.description)}

    con.row_factory = dict_factory
    return con



def sync_db(db_con):
    with open("ddl.sql") as fp:
        sql_script = fp.read()

    return db_con.executescript(sql_script)


