import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.logger import setup_logging
logger = setup_logging()

# Carregar .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_ACOES = int(os.getenv("ID_CANAL_ACOES"))
ID_CANAL_RELATORIO = int(os.getenv("ID_CANAL_RELATORIO"))

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Inicialização do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Imports dos módulos
from Comandos import contadores, slash
from Views.acao import setup_views as setup_acao_views
from Database.schema import criar_tabelas

# Setup dos módulos
contadores.setup(bot)
slash.setup(bot)

@bot.event
async def on_ready():
    GUILD_ID = 1355966070548201532
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    logger.info(f"🤖 Bot conectado como {bot.user}. Comandos sincronizados.")

    # Criar tabelas no banco
    criar_tabelas()

    # Registrar views
    setup_acao_views(bot, ID_CANAL_ACOES)

    # Restaurar metas
    from Views.meta import MetaView, gerar_embed
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if not channel.name.startswith("meta-"):
                continue
            try:
                async for msg in channel.history(limit=20):
                    if msg.author == bot.user and msg.embeds:
                        embed = msg.embeds[0]
                        if embed.title and embed.title.startswith("📦 Progresso de Meta Semanal"):
                            membro_nome = embed.title.replace("📦 Progresso de Meta Semanal - ", "").strip()
                            membro = discord.utils.get(guild.members, display_name=membro_nome)
                            if membro:
                                await msg.edit(view=MetaView(str(membro.id), membro_nome, msg))
                                logger.info(f"[✅] MetaView restaurada para {membro_nome} no canal {channel.name}")
            except Exception as e:
                logger.warning(f"[⚠️] Erro ao restaurar MetaView no canal {channel.name}: {e}")

    # Painel de Relatórios (fora do loop de canais)
    from relatorio import RelatorioView
    canal_relatorio = bot.get_channel(ID_CANAL_RELATORIO)
    if canal_relatorio:
        gif_encontrado = False

        async for msg in canal_relatorio.history(limit=50):
            if msg.author == bot.user and msg.embeds:
                embed = msg.embeds[0]
                if "📊 Painel de Relatórios" in embed.title:
                    gif_encontrado = True
                elif msg.components:
                    try:
                        await msg.delete()
                    except:
                        pass

        if not gif_encontrado:
            embed_gif = discord.Embed(
                title="📊 Painel de Relatórios",
                description="Veja os dados da familia abaixo!",
                color=discord.Color.blurple()
            )
            file = discord.File("NKgif.gif", filename="relatorio.gif")
            embed_gif.set_image(url="attachment://relatorio.gif")
            await canal_relatorio.send(embed=embed_gif, file=file)

        await canal_relatorio.send(view=RelatorioView())

bot.run(TOKEN)
#trigger redeploy