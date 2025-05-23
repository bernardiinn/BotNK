import os
import sqlite3

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # utils/
    db_path = os.path.join(base_dir, "..", "relatorio.db")  # volta pra raiz do projeto
    return sqlite3.connect(db_path)
