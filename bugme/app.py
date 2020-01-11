from db import *
from pathlib import Path

from app_config import DB_PATH



class App:
    def __init__(self, instance_path):
        self.app_path = instance_path
        self.db_path = DB_PATH
        self.db = get_connection(self.db_path)


    @classmethod
    def create_new_instance(cls, path):
        path = Path(path) / ".bugme"
        path.mkdir()

        db_file = path / "bugs.db"
        db_file.touch()

        con = get_connection(str(db_file))
        sync_db(con)
        con.close()        
        
    def create_new_defect(self, description, expected_behaviour, observed_behaviour):
        record = {
            "description": description,
            "expected_behaviour": expected_behaviour,
            "observed_behaviour": observed_behaviour,
            "status": "OPEN"
        }
        query, row = generate_insert_query("bugs", record)
        return self.db.execute(query, row).lastrowid

    def get_defect(self, defect_id):
        query = 'SELECT * FROM bugs WHERE defect_id=?;'
        row = (defect_id, )
        defect = self.db.execute(query, row).fetchall()
        if len(defect) < 1:
            raise ValueError(f"No record found for the defect with id {defect_id}")
        defect = defect[0]
        query = "SELECT * FROM comments WHERE defect_id=?;"
        comments =self.db.execute(query, row).fetchall()
        defect['comments'] = comments
        return defect


    def update_status(self, defect_id, new_status):
        query = 'UPDATE bugs SET status=? WHERE defect_id=?;'
        row = (new_status, defect_id)
        self.db.execute(query,row)


    def add_comment(self, defect_id, comments):
        record = {
            "defect_id": defect_id,
            "comment": comments
        }
        query, row = generate_insert_query('comments', record)
        self.db.execute(query, row)

    def resolve_defect(self, defect_id, resolution):
        query = "UPDATE bugs SET status='CLOSED', resolution=?, resolution_date=CURRENT_TIMESTAMP WHERE defect_id=?;"
        row = (resolution, defect_id)
        self.db.execute(query, row)

    def get_all_defects():
        query = 'SELECT * FROM bugs;'
        return self.db.execute(query)




if __name__ == '__main__':
    defect_id = int(input('Defectid: '))
    get_defect(defect_id)
    
