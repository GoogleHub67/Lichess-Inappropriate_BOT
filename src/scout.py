import sqlite3
import os
import requests
from datetime import datetime

# Dynamically locate the repository database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "config", "chess_history.db")

def scout_opponent_with_sql(username):
    """
    Checks the local SQL database for player dossiers. 
    If not found, fetches from Lichess API and logs them into SQL.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. SQL Query: Check if we already have this user scouted
    cursor.execute("SELECT weakest_format FROM opponents WHERE LOWER(username) = LOWER(?);", (username,))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        print(f"🗄️ SQL Cache Hit! Retrieved dossier for {username}. Weakness: {row[0]}")
        return row[0]
        
    # 2. Cache Miss: Fetch live data from Lichess for free
    print(f"🌐 SQL Cache Miss. Fetching live profile metrics for {username} via Lichess API...")
    url = f"https://lichess.org{username}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            perfs = data.get("perfs", {})
            
            blitz = perfs.get("blitz", {}).get("rating", 1500)
            bullet = perfs.get("bullet", {}).get("rating", 1500)
            rapid = perfs.get("rapid", {}).get("rating", 1500)
            
            # Determine weakest pool format
            ratings = {"blitz": blitz, "bullet": bullet, "rapid": rapid}
            weakest_format = min(ratings, key=ratings.get)
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 3. SQL Query: Insert new profile dossier into your local repository DB
            cursor.execute('''
                INSERT OR REPLACE INTO opponents (username, blitz_rating, bullet_rating, rapid_rating, weakest_format, last_scouted)
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (username, blitz, bullet, rapid, weakest_format, date_str))
            
            conn.commit()
            conn.close()
            print(f"💾 SQL INSERT successful! Saved player intelligence dossier for {username}.")
            return weakest_format
        else:
            conn.close()
            return "default"
    except Exception as e:
        print(f"Scout SQL Error: {e}")
        conn.close()
        return "default"
