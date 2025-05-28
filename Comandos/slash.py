import discord
from discord import app_commands
from discord.ext import commands
from relatorio import RelatorioView
from Views.meta import MetaModal, gerar_embed, MetaView
from Views.acao import EscolhaInicial
from utils.logger import logger  # ← agora está certo

def setup(bot: commands.Bot):
    @bot.tree.command(name="registrar_acao", description="Registrar uma ação da facção.")
    async def registrar_acao(interaction: discord.Interaction):
        await interaction.response.send_message(
            "Escolha o Tipo da Ação, Resultado e Tipo de Operação:",
            view=EscolhaInicial(),
            ephemeral=True
        )

    # @bot.tree.command(name="registrar_meta", description="Registrar uma entrega de meta.")
    # async def registrar_meta(interaction: discord.Interaction):
    #     await interaction.response.send_modal(MetaModal())

    @bot.tree.command(name="relatorio", description="Ver relatórios semanais ou por membro.")
    async def relatorio(interaction: discord.Interaction):
        await interaction.response.send_message(
            "Escolha uma opção abaixo:",
            view=RelatorioView(),
            ephemeral=True
        )

    @bot.tree.command(name="iniciar_meta", description="Criar painel de farm semanal neste canal.")
    async def iniciar_meta(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            membro_id = str(interaction.user.id)
            membro_nome = interaction.user.display_name

            canal = interaction.channel
            deletadas = 0
            mensagens_debug = []

            async for msg in canal.history(limit=50):
                if msg.author == bot.user and msg.embeds:
                    try:
                        await msg.delete()
                        deletadas += 1
                        mensagens_debug.append(f"🗑️ Deletada: {msg.id}")
                    except Exception as e:
                        mensagens_debug.append(f"❌ Erro ao deletar {msg.id}: {e}")

            embed = gerar_embed(membro_id, membro_nome)

            mensagem = await canal.send(embed=embed)  # envia embed primeiro
            await mensagem.edit(view=MetaView(membro_id, membro_nome, mensagem))  # adiciona view com mensagem

            log = "\n".join(mensagens_debug) or "Nenhuma mensagem encontrada."
            await interaction.followup.send(
                content=(
                    f"✅ Painel da meta criado!\n"
                    f"🧹 Mensagens apagadas: {deletadas}\n"
                    f"📜 Debug:\n```{log}```"
                ),
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"[iniciar_meta] Erro inesperado: {e}", exc_info=True)
            await interaction.followup.send("❌ Ocorreu um erro ao criar o painel da meta.", ephemeral=True)
