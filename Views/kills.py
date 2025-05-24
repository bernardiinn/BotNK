import discord
from discord.ui import View, Select, Button
from discord import Interaction
from utils.logger import logger

class AdicionarKillsDropdownView(View):
    def __init__(self, participantes, acao_id):
        super().__init__(timeout=300)
        self.participantes = participantes
        self.acao_id = acao_id
        self.kills = {str(p.id): 0 for p in participantes}
        self.current_page = 0
        self.per_page = 5
        logger.info("[Kills] View inicializada")
        self.render_page()

    def render_page(self):
        self.clear_items()
        start = self.current_page * self.per_page
        end = start + self.per_page
        current_participants = self.participantes[start:end]

        for p in current_participants:
            select = Select(
                placeholder=f"{p.display_name} - Kills",
                options=[
                    discord.SelectOption(label=str(i), value=str(i)) for i in range(11)
                ]
            )

            async def callback(interaction: Interaction, user_id=str(p.id), dropdown=select):
                self.kills[user_id] = int(dropdown.values[0])
                logger.debug(f"[Kills] {user_id} -> {dropdown.values[0]}")
                await interaction.response.defer()

            select.callback = callback
            self.add_item(select)

        if self.current_page > 0:
            botao_anterior = Button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
            async def anterior_callback(interaction: Interaction):
                self.current_page -= 1
                self.render_page()
                await interaction.response.edit_message(view=self)
            botao_anterior.callback = anterior_callback
            self.add_item(botao_anterior)

        if end < len(self.participantes):
            botao_proxima = Button(label="Próxima ➡️", style=discord.ButtonStyle.secondary)
            async def proxima_callback(interaction: Interaction):
                self.current_page += 1
                self.render_page()
                await interaction.response.edit_message(view=self)
            botao_proxima.callback = proxima_callback
            self.add_item(botao_proxima)

        confirmar = Button(label="✅ Confirmar Kills", style=discord.ButtonStyle.success)
        async def confirmar_callback(interaction: Interaction):
            logger.info(f"[Kills] Confirmado: {self.kills}")
            # Aqui você pode salvar no banco de dados se quiser
            await interaction.response.send_message("✅ Kills registradas com sucesso!", ephemeral=True)
        confirmar.callback = confirmar_callback
        self.add_item(confirmar)
