import discord
import sqlite3
from datetime import datetime, timedelta
from Views.meta import get_total_farmado, VALOR_META_SEMANAL
from mvp import calcular_top_mvp_vitorias
from utils.logger import logger
from utils.db import get_db_connection

class RelatorioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📆 Relatório Mensal", style=discord.ButtonStyle.primary, custom_id="relatorio_mensal")
    async def relatorio_mensal(self, interaction: discord.Interaction, button: discord.ui.Button):
        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT tipo_acao, resultado, operacao, data_hora, dinheiro, participantes FROM acoes')
        registros = c.fetchall()
        conn.close()

        total = vitorias = derrotas = fuga = tiro = 0
        total_dinheiro = 0
        tipos_contagem = {}
        participantes_contagem = {}

        for tipo_acao, resultado, operacao, data_hora, dinheiro, participantes in registros:
            try:
                data = datetime.strptime(data_hora.split(" - ")[0].strip(), "%d/%m/%Y")
                if data >= inicio_mes:
                    total += 1
                    tipos_contagem[tipo_acao] = tipos_contagem.get(tipo_acao, 0) + 1

                    for p in participantes.split():
                        participantes_contagem[p] = participantes_contagem.get(p, 0) + 1

                    if resultado.lower().startswith("vitória"):
                        vitorias += 1
                    elif resultado.lower() == "derrota":
                        derrotas += 1

                    if operacao.lower() == "fuga":
                        fuga += 1
                    elif operacao.lower() == "tiro":
                        tiro += 1

                    valor = int(dinheiro.replace("R$ ", "").replace(".", "").replace(",", ""))
                    total_dinheiro += valor
            except Exception:
                continue

        acao_mais_comum = max(tipos_contagem, key=tipos_contagem.get) if tipos_contagem else "N/A"
        # Carregar kills do banco
        conn = get_db_connection()
        c = conn.cursor()
        # Pegue todas as kills e filtre no Python
        c.execute("""
            SELECT k.membro_id, k.kills, a.data_hora
            FROM kills k
            JOIN acoes a ON k.acao_id = a.id
        """)
        kills_registradas = c.fetchall()

        conn.close()

        kills_por_membro = {}
        for membro_id, kills, data_hora in kills_registradas:
            try:
                data = datetime.strptime(data_hora.split(" - ")[0], "%d/%m/%Y")
                if data >= inicio_mes:  # ou inicio_mes, dependendo do relatório
                    kills = int(kills)
                    kills_por_membro[membro_id] = kills_por_membro.get(membro_id, 0) + kills
            except Exception as e:
                logger.warning(f"[ERRO KILLS] {e}")
                continue

        top_mvp = calcular_top_mvp_vitorias(inicio_mes)
        mvp_texto = ""

        medalhas = ["🥇", "🥈", "🥉"]
        for i, (membro_id, vitorias, kills) in enumerate(top_mvp):
            membro = interaction.guild.get_member(int(membro_id))
            nome = membro.display_name if membro else f"<@{membro_id}>"
            medalha = medalhas[i] if i < len(medalhas) else "⭐"
            mvp_texto += f"{medalha} {nome} — {vitorias} vitórias com {kills} kills\n"

        if not mvp_texto:
            mvp_texto = "Sem vitórias registradas."

        embed = discord.Embed(title="📆 Relatório Mensal", color=discord.Color.dark_blue())
        embed.add_field(name="📊 Total de Ações", value=str(total), inline=True)
        embed.add_field(name="🏆 Vitórias", value=f"{vitorias} ({(vitorias/total*100):.1f}%)" if total else "0", inline=True)
        embed.add_field(name="❌ Derrotas", value=str(derrotas), inline=True)
        embed.add_field(name="💣 Ações Tiro", value=str(tiro), inline=True)
        embed.add_field(name="🚗 Ações Fuga", value=str(fuga), inline=True)
        embed.add_field(name="💰 Dinheiro Total", value=f"R$ {total_dinheiro:,}".replace(",", "."), inline=True)
        embed.add_field(name="🔥 Ação Mais Comum", value=acao_mais_comum, inline=True)

        if mvp_texto:
            embed.add_field(name="🏅 Top 3 MVPs do Mês", value=mvp_texto.strip(), inline=False)
        else:
            embed.add_field(name="🏅 MVPs", value="Sem ações este mês.", inline=False)

        embed.set_footer(text="Relatório do mês atual. Baseado nas ações registradas.")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)

    @discord.ui.button(label="📅 Relatório Semanal", style=discord.ButtonStyle.primary, custom_id="relatorio_semanal")
    async def relatorio_semanal(self, interaction: discord.Interaction, button: discord.ui.Button):
        hoje = datetime.now()
        inicio_semana = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT tipo_acao, resultado, operacao, data_hora, dinheiro, participantes FROM acoes')
        registros = c.fetchall()
        conn.close()

        total = vitorias = derrotas = fuga = tiro = 0
        total_dinheiro = 0
        tipos_contagem = {}
        participantes_contagem = {}

        for tipo_acao, resultado, operacao, data_hora, dinheiro, participantes in registros:
            try:
                data = datetime.strptime(data_hora.split(" - ")[0].strip(), "%d/%m/%Y")
                if data >= inicio_semana:
                    total += 1
                    tipos_contagem[tipo_acao] = tipos_contagem.get(tipo_acao, 0) + 1
                    for p in participantes.split():
                        participantes_contagem[p] = participantes_contagem.get(p, 0) + 1

                    if resultado.lower().startswith("vitória"):
                        vitorias += 1
                    elif resultado.lower() == "derrota":
                        derrotas += 1

                    if operacao.lower() == "fuga":
                        fuga += 1
                    elif operacao.lower() == "tiro":
                        tiro += 1

                    valor = int(dinheiro.replace("R$ ", "").replace(".", "").replace(",", ""))
                    total_dinheiro += valor
            except Exception as e:
                logger.warning(f"[ERRO AÇÃO] {e}")
                continue

        acao_mais_comum = max(tipos_contagem, key=tipos_contagem.get) if tipos_contagem else "N/A"

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT k.membro_id, k.kills, a.data_hora
            FROM kills k
            JOIN acoes a ON k.acao_id = a.id
        """)
        kills_registradas = c.fetchall()
        conn.close()

        kills_por_membro = {}
        for membro_id, kills, data_hora in kills_registradas:
            try:
                data = datetime.strptime(data_hora.split(" - ")[0], "%d/%m/%Y")
                if data >= inicio_semana:
                    kills = int(kills)
                    kills_por_membro[membro_id] = kills_por_membro.get(membro_id, 0) + kills
            except Exception as e:
                logger.warning(f"[ERRO KILLS] {e}")
                continue

        top_mvp = calcular_top_mvp_vitorias(inicio_semana)
        mvp_texto = ""

        medalhas = ["🥇", "🥈", "🥉"]
        for i, (membro_id, vitorias, kills) in enumerate(top_mvp):
            membro = interaction.guild.get_member(int(membro_id))
            nome = membro.display_name if membro else f"<@{membro_id}>"
            medalha = medalhas[i] if i < len(medalhas) else "⭐"
            mvp_texto += f"{medalha} {nome} — {vitorias} vitórias com {kills} kills\n"

        if not mvp_texto:
            mvp_texto = "Sem vitórias registradas."

        embed = discord.Embed(title="📅 Relatório Semanal", color=discord.Color.blue())
        embed.add_field(name="📊 Total de Ações", value=str(total), inline=True)
        embed.add_field(name="🏆 Vitórias", value=f"{vitorias} ({(vitorias/total*100):.1f}%)" if total else "0", inline=True)
        embed.add_field(name="❌ Derrotas", value=str(derrotas), inline=True)
        embed.add_field(name="💣 Ações Tiro", value=str(tiro), inline=True)
        embed.add_field(name="🚗 Ações Fuga", value=str(fuga), inline=True)
        embed.add_field(name="💰 Dinheiro Total", value=f"R$ {total_dinheiro:,}".replace(",", "."), inline=True)
        embed.add_field(name="🔥 Ação Mais Comum", value=acao_mais_comum, inline=True)

        if mvp_texto:
            embed.add_field(name="🏅 Top 3 MVPs da Semana", value=mvp_texto.strip(), inline=False)
        else:
            embed.add_field(name="🏅 MVPs", value="Sem ações esta semana.", inline=False)

        embed.set_footer(text="Relatório da semana atual. Atualizado com base nas ações registradas.")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)


    @discord.ui.button(label="👥 Relatório por Membro", style=discord.ButtonStyle.secondary, custom_id="relatorio_membro")
    async def relatorio_membro(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT participantes FROM acoes')
        registros = c.fetchall()
        conn.close()

        membros_ids = set()
        for linha in registros:
            for membro in linha[0].split():
                membros_ids.add(membro.replace("<@", "").replace(">", ""))

        options = []
        for membro_id in membros_ids:
            member = interaction.guild.get_member(int(membro_id))
            nome = member.display_name if member else f"ID: {membro_id}"
            options.append(discord.SelectOption(label=nome, value=membro_id))

        view = MemberDropdown(options)
        await interaction.response.send_message("Selecione um membro para ver o relatório:", view=view, ephemeral=True, delete_after=180)

    @discord.ui.button(label="💸 Relatório de Metas", style=discord.ButtonStyle.success, custom_id="relatorio_metas")
    async def relatorio_metas(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT DISTINCT membro_id FROM farm_droga")
        membros = [linha[0] for linha in c.fetchall()]
        conn.close()

        if not membros:
            await interaction.response.send_message("Nenhum membro iniciou meta ainda.", ephemeral=True)
            return

        linhas = []
        for membro_id in membros:
            total = get_total_farmado(membro_id)
            falta = max(0, VALOR_META_SEMANAL - total)
            member = interaction.guild.get_member(int(membro_id))
            nome = member.display_name if member else f"<@{membro_id}>"

            if falta > 0:
                linhas.append(f"❌ {nome} — Falta: **{falta:,}K**".replace(",", "."))
            else:
                linhas.append(f"✅ {nome} — Meta atingida com **{total:,}K**".replace(",", "."))

        mensagem = "\n".join(linhas)
        embed = discord.Embed(title="💸 Progresso das Metas Semanais", description=mensagem, color=discord.Color.teal())
        embed.set_footer(text="Atualizado com base nos farms da semana atual.")

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)


class MemberDropdown(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.add_item(MemberSelect(options))


class MemberSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Escolha o membro", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        membro_id = self.values[0]
        hoje = datetime.now()
        inicio_semana = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT tipo_acao, resultado, operacao, data_hora, dinheiro, participantes FROM acoes')
        registros = c.fetchall()
        conn.close()

        total = fuga = tiro = vitorias = derrotas = 0
        total_dinheiro = 0
        total_semana = 0
        participantes_contagem = {}

        for tipo_acao, resultado, operacao, data_hora, dinheiro, participantes in registros:
            participantes_lista = participantes.split()
            for p in participantes_lista:
                participantes_contagem[p] = participantes_contagem.get(p, 0) + 1

            if f"<@{membro_id}>" in participantes_lista:
                total += 1
                try:
                    if operacao.lower() == "fuga":
                        fuga += 1
                    elif operacao.lower() == "tiro":
                        tiro += 1

                    if resultado.lower().startswith("vitória"):
                        vitorias += 1
                    elif resultado.lower() == "derrota":
                        derrotas += 1

                    valor_total = int(dinheiro.replace("R$ ", "").replace(".", "").replace(",", ""))
                    valor_individual = valor_total // len(participantes_lista)
                    total_dinheiro += valor_individual

                    data = datetime.strptime(data_hora.split('-')[0].strip(), "%d/%m/%Y")
                    if data >= inicio_semana:
                        total_semana += 1
                except:
                    continue

        # Verificar se é MVP
        top_participantes = sorted(participantes_contagem.items(), key=lambda x: x[1], reverse=True)
        eh_mvp = top_participantes and top_participantes[0][0] == f"<@{membro_id}>"

        membro = interaction.guild.get_member(int(membro_id))
        nome = membro.display_name if membro else f"<@{membro_id}>"
        titulo = f"🔁 Relatório de {nome}"
        cor = discord.Color.gold() if eh_mvp else discord.Color.purple()
        if eh_mvp:
            titulo = f"🏅 {titulo} — MVP da Semana!"

        embed = discord.Embed(title=titulo, color=cor)
        embed.add_field(name="📊 Total de Ações", value=str(total), inline=True)
        embed.add_field(name="🏆 Vitórias", value=f"{vitorias} ({(vitorias/total*100):.1f}%)" if total else "0", inline=True)
        embed.add_field(name="❌ Derrotas", value=str(derrotas), inline=True)
        embed.add_field(name="💰 Arrecadação Individual", value=f"R$ {total_dinheiro:,}".replace(",", "."), inline=True)
        embed.add_field(name="🚗 Fugas", value=str(fuga), inline=True)
        embed.add_field(name="💣 Tiros", value=str(tiro), inline=True)
        embed.add_field(name="📅 Participações esta semana", value=str(total_semana), inline=True)

        # Buscar kills do membro
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(kills) FROM kills WHERE membro_id = ?", (membro_id,))
        res = c.fetchone()
        conn.close()
        kills_total = res[0] or 0

        embed.add_field(name="🔫 Kills Registradas", value=str(kills_total), inline=True)

        from Views.meta import get_total_farmado
        farmado = get_total_farmado(membro_id)
        embed.add_field(name="🧪 Farm da Semana", value=f"{farmado:,}K".replace(",", "."), inline=True)

        embed.set_footer(text="Baseado em ações e farms da semana atual.")
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)

