from typing import final
import sqlite3
from pathlib import Path

@final
class _SqlDataConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_SqlDataConnection, cls).__new__(cls)
            cls._instance.db = None
        return cls._instance
    
    def __init__(self):
        if self.db is None:
            # Get the database path relative to this module's location
            db_path = Path(__file__).parent / 'skylab-data.db'
            self.db = sqlite3.connect(str(db_path))

    @final
    def cursor(self):
        return self.db.cursor()