import streamlit as st
import sqlite3
import pandas as pd
import os

# Locate the database file inside the repository layout
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "config", "chess_history.db")

st.set_page_config(page_title="Lichess Bot SQL Dashboard", page_icon="🤖", layout="wide")
st.title("🤖 SQL Match History Dashboard")

# Connect and read data using raw SQL queries
try:
    conn = sqlite3.connect(DB_PATH)
    
    # 1. SQL Query to get all raw match data ordered by newest first
    df = pd.read_sql_query("SELECT * FROM matches ORDER BY id DESC;", conn)
    
    # 2. SQL Queries to calculate high-speed metrics directly in the database
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches;")
    total_games = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM matches WHERE LOWER(result) = 'win';")
    wins = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM matches WHERE LOWER(result) = 'loss';")
    losses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM matches WHERE LOWER(result) = 'draw';")
    draws = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(final_cpl) FROM matches;")
    avg_cpl = cursor.fetchone()[0] or 0
    
    conn.close()
except Exception as e:
    df = pd.DataFrame()
    total_games = wins = losses = draws = avg_cpl = 0

if df.empty or total_games == 0:
    st.info("No games logged in the SQL database yet! Go play some matches on Lichess to see data.")
else:
    # 📈 Dashboard Metrics Row
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Matches (SQL COUNT)", total_games)
    col2.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}W - {losses}L")
    col3.metric("Draws", draws)
    col4.metric("Avg Centipawn Loss", f"{avg_cpl:.1f}")

    # 📊 Win/Loss Breakdown Chart
    st.subheader("📊 Performance Distribution")
    st.bar_chart(df['result'].value_counts())

    # 📜 Detailed Match Log Table
    st.subheader("📜 Raw SQL Table Contents")
    st.dataframe(
        df[['game_id', 'opponent', 'result', 'final_cpl', 'date_played']], 
        use_container_width=True
    )
