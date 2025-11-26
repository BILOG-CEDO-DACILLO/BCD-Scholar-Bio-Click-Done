import sqlite3
import os
from pathlib import Path
import bcrypt
import hashlib


class Database:
    def __init__(self):
        self.setup_paths()
        self.create_tables()
        self.data_table()

    # --- Utility Methods (Unchanged) ---
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

    def setup_paths(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parents[2]
        self.db_dir = self.project_root / "data"
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "database.db"

    def connect(self):
        return sqlite3.connect(self.db_path)

    def data_table(self):
        try:
            with self.connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS scholarships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT,
                    middle_name TEXT,
                    suffix TEXT,
                    email TEXT NOT NULL,
                    municipality TEXT NOT NULL,
                    college TEXT NOT NULL,
                    program TEXT NOT NULL,
                    year_level TEXT NOT NULL,
                    scholarship_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gwa REAL,
                    FOREIGN KEY (username) REFERENCES usersInfo (username)
                )""")
        except Exception as e:
            print(f"Error: {e}")

    def submitvalidator(self, username, scholarship_name):
        try:
            with self.connect() as conn:
                check_query = """
                    SELECT id 
                    FROM scholarships 
                    WHERE username = ? AND scholarship_name = ?
                """
                existing_record = conn.execute(check_query, (username, scholarship_name)).fetchone()

                if existing_record:
                    print(f"Error: User {username} has already applied for the {scholarship_name} scholarship.")
                    return False
                return True

        except Exception as e:
            print(f"Error in submitvalidator: {e}")
            return False

    def sumbitScholarship(self, username, first_name, last_name, middle_name, suffix, email, municipality,
                          college, program, year_level, scholarship_name, status, gwa):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()

                insert_query = """
                    INSERT INTO scholarships (
                        username, first_name, last_name, middle_name, suffix, email, municipality, college, program, year_level,
                        scholarship_name, status, gwa
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """
                cursor.execute(insert_query, (username, first_name, last_name, middle_name, suffix, email, municipality,
                                              college, program, year_level, scholarship_name, status, gwa))
                conn.commit()
                return True

        except Exception as e:
            print(f"Error submitting scholarship: {e}")
            return False

    def create_tables(self):
        try:
            with self.connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS usersInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acctype TEXT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password BLOB NOT NULL,
                scholarship_stat TEXT NOT NULL,
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
                phone_number TEXT NOT NULL)
            """)
        except sqlite3.OperationalError as e:
            print(f"Table creation error: {e}")

    # -------------- SECURE SIGNUP (Unchanged) ----------------
    def acc_validation(self, username, email):
        try:
            with self.connect() as conn:
                validator = conn.execute(
                    """SELECT id FROM usersInfo
                    WHERE username = ? OR email = ?""", (username, email)
                ).fetchone()

                return validator is None
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def handle_signup(self, acctype, username, email, password, scholarship_stat,
                      profile_photo, first_name, last_name, middle_initial, suffix,
                      civil_status, gender, date_of_birth, age, student_id, college,
                      year_level, program, municipality, phone_number):
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        profile_photo_data = self._convert_to_blob(profile_photo)

        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO usersInfo (
                        acctype, username, email, password, scholarship_stat, 
                        profile_photo_data, first_name, last_name, middle_initial, suffix, 
                        civil_status, gender, date_of_birth, age, student_id, college, 
                        year_level, program, municipality, phone_number
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        acctype, username, email, hashed_pw, scholarship_stat,
                        profile_photo_data,
                        first_name, last_name, middle_initial, suffix,
                        civil_status, gender, date_of_birth, age, student_id, college,
                        year_level, program, municipality, phone_number
                    )
                )
                conn.commit()
            return True, "User record imported successfully."

        except sqlite3.IntegrityError as e:
            return False, f"Import failed: Integrity constraint violated. Check for duplicate username, email, or student ID. Error: {e}"

        except Exception as e:
            return False, f"Database error during import: {e}"

    # ---------------------- HANDLE LOGIN (Used by login_window.py) -----------
    def handle_login(self, usernameoremail, password):
        try:
            with self.connect() as conn:
                user_record = conn.execute(
                    "SELECT password, username FROM usersInfo WHERE username = ? OR email = ?",
                    (usernameoremail, usernameoremail)
                ).fetchone()

                if not user_record:
                    # Added print for debugging login issues
                    print("LOGIN FAILED: Username/Email not found.")
                    return False

                stored_hash = user_record[0]

                if not stored_hash:
                    print("LOGIN FAILED: Stored password hash is empty.")
                    return False

                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    # SUCCESS: Return True and the actual canonical username
                    print(f"LOGIN SUCCESSFUL for user: {user_record[1]}")
                    return True, user_record[1]
                else:
                    # Added print for debugging login issues
                    print("LOGIN FAILED: Incorrect password.")
                    return False

        except Exception as e:
            print(f"CRITICAL LOGIN ERROR: {e}")
            return False

    def handle_information_data(self, usernameoremail):
        try:
            with self.connect() as conn:
                user_record = conn.execute(
                    """SELECT 
                        id, acctype, username, email, scholarship_stat, profile_photo_data,
                        first_name, last_name, middle_initial, suffix, civil_status,
                        gender, date_of_birth, age, student_id, college, 
                        year_level, program, municipality, phone_number
                    FROM usersInfo 
                    WHERE username = ? OR email = ?""",
                    (usernameoremail, usernameoremail)
                ).fetchone()

                if user_record is None:
                    print(f"Information error: User '{usernameoremail}' not found.")
                    return None

                information_list = list(user_record)

                return information_list

        except Exception as e:
            print(f"Information error: {e}")
            return None

    def get_user_scholar_status(self, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT scholarship_name, status
            FROM scholarships
            WHERE username = ?
        """, (username,))

        result = cursor.fetchall()
        conn.close()
        return result

    def get_user_info_for_admin(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, first_name, last_name, middle_name, email, municipality, 
                   college, program, year_level, scholarship_name, status, gwa, suffix
            FROM scholarships
        """)

        result = cursor.fetchall()
        conn.close()
        return result

    def is_Admin(self, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        result = cursor.execute("""SELECT acctype FROM usersInfo WHERE username = ?""", (username,)).fetchone()
        AT = result[0]
        if AT == "ADMIN":return True
        else:return False

    def update_scholarship_status(self, scholar_id, new_status):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE scholarships SET status = ? WHERE id = ?",
                    (new_status, scholar_id)
                )

                cursor.execute(
                    "SELECT username FROM scholarships WHERE id = ?",
                    (scholar_id,)
                )
                result = cursor.fetchone()
                if not result:
                    return False

                username = result[0]

                if new_status.upper() == "ACCEPTED":
                    cursor.execute(
                        "UPDATE usersInfo SET scholarship_stat = 'SCHOLAR' WHERE username = ?",
                        (username,)
                    )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error updating scholarship status: {e}")
            return False

    def get_all_scholars(self):
        self.refresh_scholar_data()
        try:
            with self.connect() as conn:
                query_stats = """
                    SELECT scholarship_stat 
                    FROM usersInfo 
                    WHERE acctype = 'STUDENT'
                """
                all_stats = [row[0] for row in conn.execute(query_stats).fetchall()]

                query_students = """
                    SELECT COUNT(*) 
                    FROM usersInfo 
                    WHERE acctype = 'STUDENT'
                """
                total_students = conn.execute(query_students).fetchone()[0]

                scholar_count = sum(1 for s in all_stats if s and s.upper() == "SCHOLAR")
                non_scholar_count = total_students - scholar_count

                chart_dict = {
                    "SCHOLAR": scholar_count,
                    "NON-SCHOLAR": non_scholar_count
                }

                table_query = """
                    SELECT COUNT(*)
                    FROM usersInfo
                    WHERE acctype = 'STUDENT'
                """
                table_data = conn.execute(table_query).fetchone()

                town_query = """
                    SELECT municipality,
                           SUM(CASE WHEN UPPER(scholarship_stat) = 'SCHOLAR' THEN 1 ELSE 0 END) AS scholars,
                           SUM(CASE WHEN UPPER(scholarship_stat) != 'SCHOLAR' OR scholarship_stat IS NULL THEN 1 ELSE 0 END) AS non_scholars
                    FROM usersInfo
                    WHERE acctype = 'STUDENT'
                    GROUP BY municipality
                """

                towns_raw = conn.execute(town_query).fetchall()
                town_dict = {
                    row[0]: {
                        "SCHOLAR": row[1],
                        "NON-SCHOLAR": row[2]
                    }
                    for row in towns_raw
                }
                return chart_dict, table_data, town_dict

        except Exception as e:
            print(f"Error getting scholar counts: {e}")
            return {"SCHOLAR": 0, "NON-SCHOLAR": 0}, [], {}

    def refresh_scholar_data(self):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()

                # 1️⃣ Reset all students to NON-SCHOLAR by default
                cursor.execute("""
                    UPDATE usersInfo
                    SET scholarship_stat = 'NON-SCHOLAR'
                    WHERE acctype='STUDENT'
                """)

                # 2️⃣ Update users with accepted scholarships to SCHOLAR
                cursor.execute("""
                    UPDATE usersInfo
                    SET scholarship_stat = 'SCHOLAR'
                    WHERE username IN (
                        SELECT username
                        FROM scholarships
                        WHERE UPPER(status) = 'ACCEPTED'
                    )
                """)

                # 3️⃣ Compute overall counts
                cursor.execute("""
                    SELECT COUNT(*) FROM usersInfo WHERE acctype='STUDENT'
                """)
                total_students = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM usersInfo WHERE acctype='STUDENT' AND scholarship_stat='SCHOLAR'
                """)
                total_scholars = cursor.fetchone()[0]

                total_non_scholars = total_students - total_scholars

                overall_counts = {
                    "SCHOLAR": total_scholars,
                    "NON-SCHOLAR": total_non_scholars
                }

                # 4️⃣ Compute municipality stats
                cursor.execute("""
                    SELECT municipality,
                           SUM(CASE WHEN scholarship_stat='SCHOLAR' THEN 1 ELSE 0 END) AS scholars,
                           SUM(CASE WHEN scholarship_stat='NON-SCHOLAR' THEN 1 ELSE 0 END) AS non_scholars
                    FROM usersInfo
                    WHERE acctype='STUDENT'
                    GROUP BY municipality
                """)
                towns_raw = cursor.fetchall()

                municipality_stats = {
                    row[0]: {"SCHOLAR": row[1], "NON-SCHOLAR": row[2]}
                    for row in towns_raw
                }

                conn.commit()
                print("Scholar data refreshed successfully.")

                return overall_counts, municipality_stats

        except Exception as e:
            print(f"Error refreshing scholar data: {e}")
            return {"SCHOLAR": 0, "NON-SCHOLAR": 0}, {}

    def get_scholarship_program_stats(self):
        self.refresh_scholar_data()
        try:
            with self.connect() as conn:
                query_program_counts = """
                    SELECT scholarship_name, COUNT(*)
                    FROM scholarships
                    WHERE status = 'ACCEPTED'
                    GROUP BY scholarship_name;
                """
                program_counts_raw = conn.execute(query_program_counts).fetchall()
                program_counts = {row[0]: row[1] for row in program_counts_raw}

                # 2. Total Scholarship Records (Replaces total student count)
                query_total_records = """
                    SELECT COUNT(*)
                    FROM scholarships
                """
                # Fetch the single count and wrap it in a tuple to match original 'table_data' structure
                total_records = conn.execute(query_total_records).fetchone()[0]
                total_records_tuple = (total_records,)

                # 3. Count by Municipality and Scholarship Program (Replaces 'town_dict')
                query_municipality_program_counts = """
                    SELECT municipality, scholarship_name, COUNT(*)
                    FROM scholarships
                    WHERE status = 'ACCEPTED'
                    GROUP BY municipality, scholarship_name
                """

                municipality_raw = conn.execute(query_municipality_program_counts).fetchall()
                municipality_program_counts = {}

                # Structure the data as:
                # {'Municipality A': {'Program X': count, 'Program Y': count}, ...}
                for municipality, program_name, count in municipality_raw:
                    if municipality not in municipality_program_counts:
                        municipality_program_counts[municipality] = {}
                    municipality_program_counts[municipality][program_name] = count

                return program_counts, total_records_tuple, municipality_program_counts

        except Exception as e:
            print(f"Error getting scholarship program counts: {e}")
            # Return empty structures in case of an error
            return {}, (0,), {}

    def filter_by_scholarship(self, scholarship_name: str) -> dict:
        # HARDCODED: List of all colleges
        ALL_COLLEGES = ["CICS", "CTE", "CHS", "CAS", "CABEIHM", "CCJE"]
        college_counts = {college: 0 for college in ALL_COLLEGES}

        try:
            # Assumes self.connect() is the only method that relies on 'self'
            with self.connect() as conn:
                query = """
                    SELECT college, COUNT(*)
                    FROM scholarships
                    WHERE scholarship_name = ?  AND status = 'ACCEPTED'
                    GROUP BY college
                """
                program_counts_raw = conn.execute(query, (scholarship_name,)).fetchall()

                # Merge database results with the initialized dictionary
                for college, count in program_counts_raw:
                    if college in college_counts:
                        college_counts[college] = count

                return college_counts

        except Exception as e:
            print(f"Error filtering by scholarship: {e}")
            # Return the zero-padded dictionary on error
            return college_counts

    def filter_by_college(self, scholarship_name: str, college_name: str) -> dict:
        # HARDCODED: Dictionary of programs per college
        PROGRAM_DATA = {
            "CICS": ["BSIT", "BSIT-BA", "BSIT-NT"],
            "CAS": ["BA Comm", "BSFT", "BSP", "BSFAS"],
            "CABEIHM": ["BSA", "BSMA", "BSBA - FM", "BSBA - MM", "BSBA - HRM", "BSHM", "BSTM"],
            "CCJE": ["BSCrim"],
            "CTE": ["BEED", "BSEd - English", "BSEd - Math", "BSEd - Sciences", "BSEd - Filipino",
                    "BSEd - Social Studies", "BPEd"],
            "CHS": ["BSN", "BSND"]
        }

        # Retrieve the list of all programs for the given college, default to empty list
        all_programs = PROGRAM_DATA.get(college_name, [])

        # Create the initial dictionary with all program counts set to 0
        program_counts = {program: 0 for program in all_programs}

        try:
            with self.connect() as conn:
                query = """
                    SELECT program, COUNT(*)
                    FROM scholarships
                    WHERE scholarship_name = ? AND college = ? AND status = 'ACCEPTED'
                    GROUP BY program
                """
                program_counts_raw = conn.execute(query, (scholarship_name, college_name)).fetchall()

                # Merge database results with the initialized dictionary
                for program, count in program_counts_raw:
                    if program in program_counts:
                        program_counts[program] = count

                return program_counts

        except Exception as e:
            print(f"Error filtering by college and scholarship: {e}")
            # Return the zero-initialized dictionary on error
            return program_counts

    # Place this method inside the Database class in app/database/database.py

    def update_user_info(self, username, acctype, profile_photo_path, first_name, last_name, middle_initial, suffix,
                         civil_status, gender, date_of_birth, age, student_id, college, year_level, program,
                         municipality, phone_number):
        """Updates all user details in the usersInfo table based on the username."""

        profile_photo_data = None
        if profile_photo_path and Path(profile_photo_path).is_file():
            try:
                with open(profile_photo_path, 'rb') as f:
                    profile_photo_data = f.read()
            except Exception as e:
                print(f"Error reading profile photo file: {e}")

        try:
            conn = self.connect()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE usersInfo SET 
                acctype = ?, profile_photo_data = ?, first_name = ?, last_name = ?, middle_initial = ?,
                suffix = ?, civil_status = ?, gender = ?, date_of_birth = ?, age = ?,
                student_id = ?, college = ?, year_level = ?, program = ?, municipality = ?, phone_number = ?
                WHERE username = ?
            """, (
                acctype, profile_photo_data, first_name, last_name, middle_initial, suffix,
                civil_status, gender, date_of_birth, age, student_id, college, year_level,
                program, municipality, phone_number, username
            ))

            conn.commit()
            conn.close()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Database error during user profile update: {e}")
            return False

    def update_password_hash(self, username: str, new_password: str) -> bool:

        hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        try:
            conn = self.connect()
            cursor = conn.cursor()

            # ASSUMING your primary user table is named 'users' and has a 'password' column
            cursor.execute("""
                UPDATE users SET 
                password = ?
                WHERE username = ?
            """, (
                hashed_password, username
            ))

            conn.commit()
            conn.close()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Database error during password update for {username}: {e}")
            return False

database = Database()
