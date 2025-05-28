import os
import logging
import shutil
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.logger import setup_logging, DiscordDMHandler

# Setup do logger
logger = setup_logging()

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID_CANAL_ACOES = int(os.getenv("ID_CANAL_ACOES"))
ID_CANAL_RELATORIO = int(os.getenv("ID_CANAL_RELATORIO"))

# Intents do bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Inicialização do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Envio de log por DM
async def enviar_dm_erro(usuario_id: int, mensagem: str):
    try:
        user = await bot.fetch_user(usuario_id)
        await user.send(mensagem)
    except Exception as e:
        logger.warning(f"[ERRO_DM] Falha ao enviar DM: {e}")

# Handler para logs em DM
ADMIN_ID = 419231481412452352  # Substitua com seu ID real
dm_handler = DiscordDMHandler(bot, ADMIN_ID, enviar_dm_erro)
dm_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"))
logger.addHandler(dm_handler)

# Importação e setup de módulos
from Comandos import contadores, slash, debug
from Views.acao import setup_views as setup_acao_views
from Database.schema import criar_tabelas

contadores.setup(bot)
slash.setup(bot)
debug.setup(bot)

@bot.event
async def on_ready():
    GUILD_ID = 1355966070548201532  # Substitua se necessário
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    
    logger.info(f"🤖 Bot conectado como {bot.user}. Comandos sincronizados.")
    logger.info(f"📁 Diretório de trabalho: {os.getcwd()}")
    logger.info(f"📄 Caminho do banco: {os.path.abspath('relatorio.db')}")

    # Restaurar o banco se necessário
    if not os.path.exists("relatorio.db") or os.path.getsize("relatorio.db") < 10000:
        shutil.copyfile("relatorio_backup.db", "relatorio.db")
        logger.warning("🔁 Banco restaurado automaticamente a partir de relatorio_backup.db")

    # Criar tabelas
    criar_tabelas()

    # Setup das views de ações
    setup_acao_views(bot, ID_CANAL_ACOES)

    # Restaurar painéis de metas
    from Views.meta import MetaView
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
                                logger.info(f"✅ MetaView restaurada para {membro_nome} no canal {channel.name}")
            except Exception as e:
                logger.error(f"Erro ao restaurar MetaView no canal {channel.name}: {e}")

    # Painel de Relatórios
    from relatorio import RelatorioView
    canal_relatorio = bot.get_channel(ID_CANAL_RELATORIO)
    if canal_relatorio:
        await canal_relatorio.purge(limit=100, check=lambda m: m.author == bot.user)

        embed_gif = discord.Embed(
            title="📊 Painel de Relatórios",
            description="Veja os dados da familia abaixo!",
            color=discord.Color.blurple()
        )
        file = discord.File("NKgif.gif", filename="relatorio.gif")
        embed_gif.set_image(url="attachment://relatorio.gif")

        await canal_relatorio.send(embed=embed_gif, file=file)
        await canal_relatorio.send(view=RelatorioView())

# Rodar bot
bot.run(TOKEN)
