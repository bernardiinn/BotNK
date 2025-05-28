import os
import sqlite3

def get_db_connection():
    db_path = os.getenv("DB_PATH", "relatorio.db")  # Usa /data/relatorio.db na Railway, fallback para local
    return sqlite3.connect(db_path)
