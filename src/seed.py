"""
seed.py  —  Run this ONCE after cloning the repo.

    python seed.py

Creates the database, tables, and a default demo account using
whatever salt is generated on THIS machine.
"""

import sys
import os

SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if os.path.exists(SRC_DIR):
    sys.path.insert(0, SRC_DIR)

from database.init_db import init_db
from services.user_service import UserService


def seed():
    print("Initializing database...")
    init_db()

    svc = UserService()
    svc.init_users_table() 

    print()
    print("=" * 40)
    print("  Setup complete. You can now run the app.")
    print()
    print("  Default account:")
    print("    Username : demo")
    print("    Password : demo1234")
    print("=" * 40)


if __name__ == "__main__":
    seed()