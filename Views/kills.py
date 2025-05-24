import discord
from discord.ui import View, Select, Button
from discord import Interaction
from utils.logger import logger

class KillDropdown(Select):
    def __init__(self, participante: discord.Member):
        self.participante = participante
        options = [
            discord.SelectOption(label=str(i), value=str(i)) for i in range(11)
        ]
        super().__init__(
            placeholder=f"{participante.display_name} - Kills",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: Interaction):
        view: AdicionarKillsDropdownView = self.view
        view.kills[str(self.participante.id)] = int(self.values[0])
        logger.debug(f"[Kills] {self.participante.display_name} -> {self.values[0]}")
        await interaction.response.defer()

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
            self.add_item(KillDropdown(p))

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
            await interaction.response.send_message("✅ Kills registradas com sucesso!", ephemeral=True)
        confirmar.callback = confirmar_callback
        self.add_item(confirmar)
