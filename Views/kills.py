import discord
from discord.ui import View, Button, Modal, TextInput
from discord import Interaction
from utils.logger import logger

class KillsPorParticipanteModal(Modal):
    def __init__(self, participante: discord.Member, acao_id: int, salvar_callback):
        super().__init__(title=f"Registrar Kills para {participante.display_name}")
        self.participante = participante
        self.acao_id = acao_id
        self.salvar_callback = salvar_callback
        self.kills_input = TextInput(
            label=f"Quantas kills {participante.display_name} fez?",
            placeholder="Ex: 3",
            required=True
        )
        self.add_item(self.kills_input)

    async def on_submit(self, interaction: Interaction):
        try:
            kills = int(self.kills_input.value)
            logger.info(f"[KillsModal] {self.participante.display_name} -> {kills} kills")
            await self.salvar_callback(interaction, self.participante, self.acao_id, kills)
        except ValueError:
            await interaction.response.send_message("❌ Valor inválido. Digite um número.", ephemeral=True)

class AdicionarKillsPorBotaoView(View):
    def __init__(self, participantes: list[discord.Member], acao_id: int, salvar_callback):
        super().__init__(timeout=None)
        self.participantes = participantes
        self.acao_id = acao_id
        self.salvar_callback = salvar_callback
        logger.info("[KillsBotaoView] Criando botões de kill por participante")

        for p in participantes:
            button = Button(label=f"➕ Kills de {p.display_name}", style=discord.ButtonStyle.primary)

            async def callback(interaction: Interaction, participante=p):
                logger.debug(f"[KillsBotaoView] Abrindo modal para {participante.display_name}")
                await interaction.response.send_modal(
                    KillsPorParticipanteModal(participante, self.acao_id, self.salvar_callback)
                )

            button.callback = callback
            self.add_item(button)
