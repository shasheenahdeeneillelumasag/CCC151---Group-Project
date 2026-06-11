"""
services/user_service.py

Handles user registration, login validation, and password hashing.
Drop this file into your services/ directory.
"""

import hashlib
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'healthlink.db')


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _hash(password: str) -> str:
    """SHA-256 hash with a fixed per-installation salt stored beside the db."""
    salt_path = os.path.join(os.path.dirname(DB_PATH), '.salt')
    if not os.path.exists(salt_path):
        salt = os.urandom(32).hex()
        with open(salt_path, 'w') as f:
            f.write(salt)
    else:
        with open(salt_path) as f:
            salt = f.read().strip()
    return hashlib.sha256((salt + password).encode()).hexdigest()


@dataclass
class User:
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    patient_code: str | None = None


class UserService:

    def init_users_table(self):
        """Create the users table if it doesn't exist and seed a demo account."""
        with _get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email         TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    first_name    TEXT NOT NULL,
                    last_name     TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    patient_code  TEXT DEFAULT NULL
                )
            """)
            try:
                conn.execute("ALTER TABLE users ADD COLUMN patient_code TEXT DEFAULT NULL")
            except Exception:
                pass 
            conn.commit()

            count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count == 0:
                self.register(
                    first_name="Demo",
                    last_name="User",
                    email="demo@healthlink.local",
                    username="demo",
                    password="demo1234",
                )
                try:
                    from services.patient_service import PatientService
                    patient = PatientService().register_patient(
                        first_name="Demo",
                        last_name="User",
                        birthdate="2000-01-01",
                        sex="Male",
                    )
                    self.link_patient("demo", patient.patient_code)
                except Exception:
                    pass 

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        username: str,
        password: str,
    ) -> tuple[bool, str]:
        """
        Register a new user.
        Returns (True, "") on success or (False, error_message) on failure.
        """
        try:
            with _get_conn() as conn:
                conn.execute(
                    """INSERT INTO users
                       (username, email, first_name, last_name, password_hash)
                       VALUES (?, ?, ?, ?, ?)""",
                    (username.strip(), email.strip().lower(),
                     first_name.strip(), last_name.strip(),
                     _hash(password)),
                )
                conn.commit()
            return True, ""
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                return False, "Username is already taken."
            if "email" in str(e).lower():
                return False, "An account with that email already exists."
            return False, "Registration failed. Please try again."

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Validate credentials.
        Returns a User on success, or None if credentials are wrong.
        """
        with _get_conn() as conn:
            row = conn.execute(
                """SELECT user_id, username, email, first_name, last_name,
                          password_hash, patient_code
                   FROM users WHERE username = ?""",
                (username.strip(),),
            ).fetchone()

        if row is None:
            return None

        user_id, uname, email, first, last, stored_hash, patient_code = row
        if stored_hash != _hash(password):
            return None

        return User(user_id, uname, email, first, last, patient_code)

    def link_patient(self, username: str, patient_code: str):
        """Store the patient_code against a user account after profile creation."""
        with _get_conn() as conn:
            conn.execute(
                "UPDATE users SET patient_code = ? WHERE username = ?",
                (patient_code, username.strip()),
            )
            conn.commit()

    def username_exists(self, username: str) -> bool:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,)
            ).fetchone()
        return row is not None

    def email_exists(self, email: str) -> bool:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()
        return row is not None