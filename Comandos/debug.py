from discord.ext import commands
from utils.db import get_db_connection

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

            await ctx.send(mensagem)

        except Exception as e:
            await ctx.send(f"❌ Erro ao acessar o banco: `{e}`")
