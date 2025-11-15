import sqlite3
import os
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox


class Database:
    def __init__(self):
        # Database path
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parents[2]
        self.db_dir = project_root / "data"
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "database.db"

        # Check for corruption
        if self.db_path.exists():
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("SELECT name FROM sqlite_master;")
            except sqlite3.DatabaseError:
                print("Database corrupted! Recreating...")
                if conn:
                    conn.close()
                os.remove(self.db_path)
            finally:
                if conn:
                    conn.close()

        # Create tables

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        query = """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )"""
        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                conn.execute(query)
                print("Table created successfully")
        except Exception as e:
            print(f"Failed to create table: {e}")
        finally:
            conn.close()

   #----------------- REGISTER ---------------------------
    def handle_signup_data(self, username, email, password):
        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password)
                )
                print(f"Successfully signed up user: {username}")
                return True
        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            if "username" in msg:
                return False, "Username already exists."
            if "email" in msg:
                return False, "Email already exists."
            return False, "Integrity error."
        except Exception as e:
            return False, f"Unexpected database error: {e}"
        finally:
            conn.close()

    def handle_login_data(self, username, password):
        conn = sqlite3.connect(self.db_path)

        query1 = f"""SELECT * FROM users WHERE username = ? AND password = ?"""
        try:
            with conn:
                user = conn.execute(query1, (username, password)).fetchone()
                if user[1] == username and user[3] == password:
                    print(f"Successfully logged in: {user}")
                    return user
        except Exception as e:
            print(f"Failed to login user: {e}")
            return False
        finally:
            conn.close()
# Initialize
database = Database()
