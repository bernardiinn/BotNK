from discord.ext import commands
from utils.db import get_db_connection
import os
import shutil

def setup(bot):
    @bot.command(name="debugdb")
    async def debug_db(ctx):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT id, tipo_acao, resultado, data_hora, dinheiro FROM acoes ORDER BY id DESC LIMIT 5")
            registros = c.fetchall()
            conn.close()

            if not registros:
                await ctx.send("📭 Nenhuma ação registrada no banco.")
                return

            mensagem = "**📋 Últimas ações registradas:**\n"
            for id_, tipo, resultado, data, dinheiro in registros:
                mensagem += f"• `#{id_}` | **{tipo}** | {resultado} | {data} | {dinheiro}\n"

            await ctx.send(mensagem[:2000])

        except Exception as e:
            await ctx.send(f"❌ Erro ao acessar o banco: `{e}`")

    @bot.command(name="verdb")
    async def ver_db(ctx):
        try:
            conn = get_db_connection()
            c = conn.cursor()

            mensagem = "**📦 Banco de Dados - Visualização Rápida**\n"

            # Ações
            c.execute("SELECT id, tipo_acao, resultado, data_hora, dinheiro FROM acoes ORDER BY id DESC LIMIT 5")
            acoes = c.fetchall()
            mensagem += "\n**🗂️ Últimas Ações (acoes):**\n"
            if acoes:
                for a in acoes:
                    mensagem += f"• `#{a[0]}` {a[1]} | {a[2]} | {a[3]} | {a[4]}\n"
            else:
                mensagem += "Nenhuma ação registrada.\n"

            # Kills
            c.execute("SELECT acao_id, membro_id, kills FROM kills ORDER BY acao_id DESC LIMIT 5")
            kills = c.fetchall()
            mensagem += "\n**🔫 Kills (kills):**\n"
            if kills:
                for k in kills:
                    mensagem += f"• Ação #{k[0]} — <@{k[1]}> → {k[2]} kills\n"
            else:
                mensagem += "Nenhuma kill registrada.\n"

            # Metas
            c.execute("SELECT membro_id, valor, data FROM farm_droga ORDER BY id DESC LIMIT 5")
            metas = c.fetchall()
            mensagem += "\n**💸 Farms (farm_droga):**\n"
            if metas:
                for m in metas:
                    mensagem += f"• <@{m[0]}> — {m[1]}K em {m[2]}\n"
            else:
                mensagem += "Nenhum farm registrado.\n"

            conn.close()
            await ctx.send(mensagem[:2000])

        except Exception as e:
            await ctx.send(f"❌ Erro ao acessar o banco: `{e}`")

    @bot.command(name="restoredb")
    async def restore_db(ctx):
        if not os.path.exists("relatorio_backup.db"):
            await ctx.send("❌ Backup não encontrado (`relatorio_backup.db`).")
            return

        try:
            shutil.copyfile("relatorio_backup.db", "relatorio.db")
            await ctx.send("✅ Banco de dados restaurado com sucesso a partir do backup!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao restaurar o banco: `{e}`")
    
    @bot.command(name="ls")
    async def listar_arquivos(ctx):
        try:
            arquivos = os.listdir(".")
            if not arquivos:
                await ctx.send("📂 Nenhum arquivo encontrado no diretório atual.")
                return

            lista_formatada = "\n".join(f"• `{nome}`" for nome in arquivos)
            await ctx.send(f"📁 **Arquivos em `/app`:**\n{lista_formatada[:2000]}")

        except Exception as e:
            await ctx.send(f"❌ Erro ao listar arquivos: `{e}`")
