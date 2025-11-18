import sqlite3
import os
from pathlib import Path


class DBuserfillup:
    def __init__(self):
        self.setup_paths()
        self.create_table()

    def setup_paths(self):
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parents[2]
        self.db_dir = project_root / "data"
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "database.db"

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _convert_to_blob(self, path: str) -> bytes:
        if not path or not Path(path).is_file():
            print(f"Warning: Photo path '{path}' is invalid or file does not exist.")
            return b''
        try:
            with open(path, 'rb') as file:
                return file.read()
        except IOError as e:
            print(f"Error reading image file {path}: {e}")
            return b''

    def create_table(self):
        try:
            with self.connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS user_profile (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 

                    profile_photo_data BLOB,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    middle_initial TEXT,
                    suffix TEXT,
                    civil_status TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL, 
                    age INTEGER NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    college TEXT NOT NULL,
                    year_level TEXT NOT NULL,
                    program TEXT NOT NULL,
                    municipality TEXT NOT NULL,
                    phone_number TEXT NOT NULL,

                    FOREIGN KEY (user_id) REFERENCES users(id)
                )""")
                print("Table 'user_profile' created successfully.")
        except sqlite3.OperationalError as e:
            print(f"Error creating table: {e}")

    def fillform(self, userprofilephoto, userfirstname, userlastname,
                 usermiddlename, usersuffix, usercivilstatus,
                 usergender, userbirthday, userage, userstudentID,
                 usercollege, useryearlevel, userprogram,
                 usermunicipality, userphoneno):

        photo_blob = self._convert_to_blob(userprofilephoto)

        data = (
            photo_blob, userfirstname, userlastname, usermiddlename,
            usersuffix, usercivilstatus, usergender, userbirthday,
            userage, userstudentID, usercollege, useryearlevel,
            userprogram, usermunicipality, userphoneno
        )

        try:
            with self.connect() as conn:
                conn.execute("""
                    INSERT INTO user_profile (
                        profile_photo_data, first_name, last_name, middle_initial,
                        suffix, civil_status, gender, date_of_birth, age,
                        student_id, college, year_level, program,
                        municipality, phone_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)

                conn.commit()

            print(f"[OK] Inserted profile: {userfirstname} {userlastname}")
            return True

        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Database integrity issue: {e}")
            return False

        except sqlite3.Error as e:
            print(f"[ERROR] SQLite execution error: {e}")
            return False

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False

database = DBuserfillup()
