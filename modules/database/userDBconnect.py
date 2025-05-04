import sqlite3
import os

class VocabularyDB:
    def __init__(self, db_path="user_data/users.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_user(self, user_name):

        
    
