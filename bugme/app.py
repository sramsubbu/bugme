from db import *
from pathlib import Path


def get_app_instance():
    p = Path.cwd()
    parent = p.parent

    while p != parent:
        bgme_path = p / '.bugme'
        if bgme_path.exists():
            return bgme_path
        p = parent
        parent = p.parent

    return None
    


def create_new_defect(description, expected_behaviour, observed_behaviour):
    record = {
        "description": description,
        "expected_behaviour": expected_behaviour,
        "observed_behaviour": observed_behaviour,
        "status": "OPEN"
    }

    con = get_connection()
    query, row = generate_insert_query("bugs", record)
    res = con.execute(query, row)
    con.commit()
    return res.lastrowid


def get_defect(defect_id):
    query = 'SELECT * FROM bugs WHERE defect_id=?;'
    con = get_connection()
    row = (defect_id,)
    defect = con.execute(query,row).fetchall()
    if len(defect) < 1:
        raise ValueError(f"No record found for the defect with id {defect_id}")
    defect = defect[0]
    query = 'SELECT * FROM comments WHERE defect_id=?;'
    comments = con.execute(query, row).fetchall()

    defect['comments'] = comments

    return defect


# updating the defect can mean update status, add comments or resolve the defect
def update_status(defect_id, new_status):
    query = 'UPDATE bugs SET status=? WHERE defect_id=?;'
    con = get_connection()
    row = (new_status, defect_id)
    con.execute(query, row)
    con.commit()


def add_comment(defect_id, comments):
    record = {
        'defect_id': defect_id,
        'comment': comments
    }

    query, row = generate_insert_query('comments', record)
    con = get_connection()
    con.execute(query, row)
    con.commit()


def resolve_defect(defect_id, resolution):
    query = "UPDATE bugs SET status='CLOSED', resolution=?,resolution_date=CURRENT_TIMESTAMP WHERE defect_id=?;"
    row = (resolution, defect_id)
    con = get_connection()
    con.execute(query, row)
    con.commit()



def get_all_defects():
    con = get_connection()
    query = 'SELECT * FROM bugs;'
    res = con.execute(query).fetchall()
    return res



if __name__ == '__main__':
    defect_id = int(input('Defectid: '))
    get_defect(defect_id)
    
