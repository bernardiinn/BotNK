import sqlite3
from datetime import datetime, timedelta

def get_inicio_semana():
    hoje = datetime.now()
    return hoje - timedelta(days=hoje.weekday())

def calcular_top_mvp_vitorias(inicio=None, limite=3):
    if not inicio:
        inicio = get_inicio_semana()

    from utils.db import get_db_connection
    conn = get_db_connection()

    c = conn.cursor()

    # Buscar vitórias da semana
    c.execute("""
        SELECT id, data_hora, participantes, resultado
        FROM acoes
        WHERE LOWER(resultado) LIKE 'vitória%'
    """)
    registros = c.fetchall()

    vitorias_por_membro = {}
    acoes_validas = []

    for acao_id, data_hora, participantes, _ in registros:
        try:
            data = datetime.strptime(data_hora.split(" - ")[0], "%d/%m/%Y")
            if data >= inicio:
                acoes_validas.append(acao_id)
                for membro in participantes.split():
                    membro_id = membro.replace("<@", "").replace(">", "")
                    vitorias_por_membro[membro_id] = vitorias_por_membro.get(membro_id, 0) + 1
        except:
            continue

    if not vitorias_por_membro:
        conn.close()
        return []

    # Buscar kills para desempate
    kills_por_membro = {}
    if acoes_validas:
        placeholder = ",".join("?" * len(acoes_validas))
        c.execute(f"""
            SELECT membro_id, SUM(kills)
            FROM kills
            WHERE acao_id IN ({placeholder})
            GROUP BY membro_id
        """, acoes_validas)
        for membro_id, soma_kills in c.fetchall():
            kills_por_membro[membro_id] = soma_kills

    conn.close()

    # Ordenar por vitórias e kills (desempate)
    ranking = sorted(
        vitorias_por_membro.items(),
        key=lambda item: (item[1], kills_por_membro.get(item[0], 0)),
        reverse=True
    )

    top = []
    for membro_id, vitorias in ranking[:limite]:
        kills = kills_por_membro.get(membro_id, 0)
        top.append((membro_id, vitorias, kills))

    return top
