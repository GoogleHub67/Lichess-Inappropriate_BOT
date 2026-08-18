import sqlite3
import os
from datetime import datetime

class HistoryManager:
    def __init__(self):
        # Dynamically locate the repository root path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, "config", "chess_history.db")
        
        # Ensure the 'config' folder exists inside your repo layout
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        """Executes raw SQL to create all tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Your existing matches history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT UNIQUE,
                opponent TEXT,
                result TEXT,
                final_cpl INTEGER,
                date_played TEXT
            );
        ''')
        
        # 2. NEW: Opponent scouting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opponents (
                username TEXT PRIMARY KEY,
                blitz_rating INTEGER,
                bullet_rating INTEGER,
                rapid_rating INTEGER,
                weakest_format TEXT,
                last_scouted TEXT
            );
        ''')
        conn.commit()
        conn.close()
        
    def log_game(self, game_id, opponent, result, final_cpl):
        """Executes raw SQL INSERT to save finished games inside the repo."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Raw SQL Insertion string
            sql_query = '''
                INSERT OR IGNORE INTO matches (game_id, opponent, result, final_cpl, date_played)
                VALUES (?, ?, ?, ?, ?);
            '''
            
            cursor.execute(sql_query, (game_id, opponent, result, final_cpl, date_str))
            conn.commit()
            conn.close()
            print(f" Successfully executed SQL INSERT for game: {game_id}")
        except Exception as e:
            print(f"SQL Execution Error: {e}")
