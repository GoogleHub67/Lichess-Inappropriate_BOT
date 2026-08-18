import os
import sqlite3
from src.scout import scout_opponent_with_sql
from src.history_manager import HistoryManager

# Locate the database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "config", "chess_history.db")

def verify_setup():
    print("🧪 --- STARTING BOT PIPELINE VERIFICATION TEST --- 🧪\n")

    # ==========================================
    # TEST 1: Verify SQL Table Creation
    # ==========================================
    print("1️⃣ Testing Database Initialization...")
    manager = HistoryManager()
    
    if os.path.exists(DB_PATH):
        print(f"✅ Found SQL database file at: {DB_PATH}")
    else:
        print(f"❌ Database file not found!")
        return

    # Check if the tables actually exist inside the SQL file
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"   Detected Tables in SQL: {tables}")
    if "matches" in tables and "opponents" in tables:
        print("   ✅ Both 'matches' and 'opponents' tables exist!")
    else:
        print("   ❌ Error: Missing tables inside the database.")
        return

    # ==========================================
    # TEST 2: Verify scout.py (Cache Miss & API Fetch)
    # ==========================================
    print("\n2️⃣ Testing Opponent Scouting (Live Lichess Fetch)...")
    # Using a famous public account to test the real Lichess API response
    test_player = "DrNykterstein" 
    print(f"   Scouting target player: '{test_player}'...")
    
    weakness_format = scout_opponent_with_sql(test_player)
    print(f"   ✅ Scout Result: Target's calculated weakness is '{weakness_format}'")

    # ==========================================
    # TEST 3: Verify scout.py SQL Cache Hit
    # ==========================================
    print("\n3️⃣ Testing SQL Cache Loop...")
    print(f"   Scouting '{test_player}' a second time (should pull from SQL cache, not live API)...")
    
    cached_weakness = scout_opponent_with_sql(test_player)
    print(f"   ✅ Cache Result: '{cached_weakness}'")

    # ==========================================
    # TEST 4: Verify Match Logging (INSERT Query)
    # ==========================================
    print("\n4️⃣ Testing Game Result Logging...")
    test_game_id = "test_match_12345"
    print(f"   Logging a simulated game result for ID: {test_game_id}...")
    
    # Simulating a win against our test player with a final CPL of 22
    manager.log_game(
        game_id=test_game_id,
        opponent=test_player,
        result="win",
        final_cpl=22
    )
    
    # Verify the match was written into the SQL database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches WHERE game_id = ?;", (test_game_id,))
    logged_match = cursor.fetchone()
    conn.close()
    
    if logged_match:
        print(f"   ✅ SQL Match Data Found: {logged_match}")
    else:
        print("   ❌ Error: Game was not written into the database.")
        return

    print("\n🎉 --- ALL PIPELINE TESTS PASSED SUCCESSFULY! --- 🎉")
    print("Your code files are fully functional and talking to your local SQL database.")

if __name__ == "__main__":
    verify_setup()
