CREATE TABLE bugs(
   defect_id INTEGER PRIMARY KEY AUTOINCREMENT,
   description TEXT NOT NULL,
   expected_behaviour TEXT,
   observed_behaviour TEXT,
   created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   status  TEXT CHECK (status IN ("OPEN", "IN_PROGRESS", "CLOSED")),
   resolution TEXT,
   resolution_date DATETIME
);

CREATE TABLE comments(
   comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
   defect_id INTEGER,
   comment TEXT,
   created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY(defect_id) REFERENCES bugs(defect_id)
);
