from discord.ext import commands
import sqlite3

def setup(bot):
    @bot.command(name="magrao")
    async def magrao(ctx):
        await contar(ctx, 'magrao', "🤡 Magrao foi otário/carente/pederasta/desnecessário {} vezes.")

    @bot.command(name="bernardin")
    async def bernardin(ctx):
        await contar(ctx, 'bernardin', "💀 Bernardin morreu {} vezes.")

    @bot.command(name="leon")
    async def leon(ctx):
        await contar(ctx, 'leon', "😹 Leon foi burro/lerdão/kitty/doidao/lesado/baiano {} vezes.")

    @bot.command(name="jhon")
    async def jhon(ctx):
        await contar(ctx, 'jhon', "🤐 Jhon foi ditador {} vezes.")

    @bot.command(name="texas")
    async def texas(ctx):
        await contar(ctx, 'texas', "🐂 Texas foi altamente gado na situacao {} vezes.")

    @bot.command(name="marsola")
    async def marsola(ctx):
        conn = sqlite3.connect('relatorio.db')
        c = conn.cursor()
        nomes = ['magrao', 'bernardin', 'leon', 'jhon', 'texas']
        total = 0
        for nome in nomes:
            c.execute("INSERT OR IGNORE INTO contadores (nome, valor) VALUES (?, 0)", (nome,))
            c.execute("SELECT valor FROM contadores WHERE nome = ?", (nome,))
            total += c.fetchone()[0]
        conn.close()
        xingamentos = "burro/lerdão/kitty/doidao/lesado/baiano otário/carente/pederasta/desnecessário morto ditador gado"
        await ctx.send(f"🧠 Marsola foi {xingamentos} {total} vezes.")

    async def contar(ctx, nome, mensagem):
        conn = sqlite3.connect('relatorio.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO contadores (nome, valor) VALUES (?, 0)", (nome,))
        c.execute("UPDATE contadores SET valor = valor + 1 WHERE nome = ?", (nome,))
        c.execute("SELECT valor FROM contadores WHERE nome = ?", (nome,))
        valor = c.fetchone()[0]
        conn.commit()
        conn.close()
        await ctx.send(mensagem.format(valor))
