import sqlite3
from utils.logger import logger

def criar_tabelas():
    from utils.db import get_db_connection
    conn = get_db_connection()
    # Verifica se a conexão foi bem-sucedida
    if conn is None:
        logger.error("❌ Não foi possível conectar ao banco de dados.")
        return
    logger.info("✅ Conexão com o banco de dados estabelecida.")

    cursor = conn.cursor()

    # Tabela de ações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_acao TEXT NOT NULL,
            resultado TEXT NOT NULL,
            operacao TEXT NOT NULL,
            dinheiro TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            participantes TEXT NOT NULL
        )
    """)

    # Tabela de kills
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kills (
            acao_id INTEGER,
            membro_id TEXT,
            kills INTEGER,
            PRIMARY KEY (acao_id, membro_id)
        )
    """)

    # Tabela de metas (farm)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farm_droga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            membro_id TEXT NOT NULL,
            valor INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)

    # Tabela de contadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contadores (
            nome TEXT PRIMARY KEY,
            valor INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    logger.info("✅ Todas as tabelas foram criadas ou já existiam.")
