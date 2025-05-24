import discord
from discord.ui import View, Select, Button

MAX_COMPONENTS_PER_PAGE = 5

class KillDropdown(Select):
    def __init__(self, user):
        options = [
            discord.SelectOption(label=str(i), value=str(i)) for i in range(0, 11)
        ]
        super().__init__(
            placeholder=f"Kills de {user.display_name}",
            min_values=1,
            max_values=1,
            options=options
        )
        self.user_id = user.id

    async def callback(self, interaction: discord.Interaction):
        view: AdicionarKillsDropdownView = self.view
        view.kills[str(self.user_id)] = int(self.values[0])
        await interaction.response.defer()

class AdicionarKillsDropdownView(View):
    def __init__(self, participantes, acao_id):
        super().__init__(timeout=300)
        self.participantes = participantes
        self.acao_id = acao_id
        self.page = 0
        self.kills = {}
        self.total_pages = (len(participantes) + MAX_COMPONENTS_PER_PAGE - 1) // MAX_COMPONENTS_PER_PAGE
        self.render_page()

    def render_page(self):
        self.clear_items()
        start = self.page * MAX_COMPONENTS_PER_PAGE
        end = start + MAX_COMPONENTS_PER_PAGE
        for membro in self.participantes[start:end]:
            self.add_item(KillDropdown(membro))

        if self.page > 0:
            self.add_item(Button(label="⬅️ Anterior", style=discord.ButtonStyle.primary, custom_id="anterior"))
        if self.page < self.total_pages - 1:
            self.add_item(Button(label="Próxima ➡️", style=discord.ButtonStyle.primary, custom_id="proxima"))

        self.add_item(Button(label="✅ Confirmar Kills", style=discord.ButtonStyle.success, custom_id="confirmar"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Permitir que qualquer um interaja. Pode-se restringir por autor se desejar.

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, custom_id="")
    async def on_button_click(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        if custom_id == "anterior":
            self.page -= 1
        elif custom_id == "proxima":
            self.page += 1
        elif custom_id == "confirmar":
            await interaction.response.send_message(f"Kills registradas: {self.kills}", ephemeral=True)
            self.stop()
            return
        self.render_page()
        await interaction.response.edit_message(view=self)

# Exemplo de uso no bot ao registrar a ação:
# view = AdicionarKillsDropdownView(participantes, acao_id)
# await canal.send("Adicione os kills de cada membro:", view=view)
