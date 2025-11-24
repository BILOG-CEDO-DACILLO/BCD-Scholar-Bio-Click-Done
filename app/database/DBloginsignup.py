import sqlite3
import os
from pathlib import Path
import bcrypt


class Database:
    def __init__(self):
        self. setup_paths()
        self.create_tables()

    def setup_paths(self):
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parents[2]
        self.db_dir = project_root / "data"
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "database.db"

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            scholarship_stat TEXT NOT NULL
        )
        """

        with self.connect() as conn:
            conn.execute(query)

    # -------------- SECURE SIGNUP ----------------
    def handle_signup_data(self, username, email, password, scholarship_stat):
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            with self.connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, email, password, scholarship_stat) VALUES (?, ?, ?, ?)",
                    (username, email, hashed_pw, scholarship_stat),
                )
            return True
        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            if "username" in msg:
                return False, "Username already exists."
            if "email" in msg:
                return False, "Email already exists."
            return False, "Integrity error."
        except Exception as e:
            return False, f"Database error: {e}"

    # -------------- SECURE LOGIN ----------------
    def handle_login_data(self, username, password):
        try:
            with self.connect() as conn:
                user = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,)
                ).fetchone()

            if not user:
                return False

            stored_hash = user[3]

            if bcrypt.checkpw(password.encode(), stored_hash):
                return user
            else:
                return False

        except Exception as e:
            print(f"Login error: {e}")
            return False

    def handle_information_data(self, username):
        try:
            with self.connect() as conn:
                user = conn.execute(
                    "SELECT id, email FROM users WHERE username = ?", [username]).fetchone()
                user_id = user[0]
                information = []
                user_infos = conn.execute("SELECT * FROM user_profile WHERE user_id = ?", [user_id]).fetchone()
                for info in user_infos:
                    information.append(info)
                information.append(user[1])
                return information
        except Exception as e:
            print(f"Information error: {e}")
database = Database()
