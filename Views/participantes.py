import discord
from discord.ui import View, Select, Button
from Views.acao import enviar_acao_completa
import sqlite3
from utils.logger import logger

class PaginatedSelectView(View):
    def __init__(self, tipo_acao, resultado, operacao, data_hora, dinheiro, guild):
        super().__init__(timeout=600)
        self.tipo_acao = tipo_acao
        self.resultado = resultado
        self.operacao = operacao
        self.data_hora = data_hora
        self.dinheiro = dinheiro
        self.guild = guild

        self.current_page = 0
        self.members_per_page = 20
        self.selected_members = set()
        self.total_pages = (len(guild.members) // self.members_per_page) + 1

        self.render_page()

    def render_page(self):
        self.clear_items()

        start = self.current_page * self.members_per_page
        end = start + self.members_per_page
        membros_pagina = [m for m in self.guild.members if not m.bot][start:end]

        options = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in membros_pagina]

        select = Select(placeholder="Selecione os participantes", options=options, min_values=1, max_values=len(options))

        async def select_callback(interaction: discord.Interaction):
            self.selected_members.update(select.values)
            await interaction.response.defer()

        select.callback = select_callback
        self.add_item(select)

        if self.current_page > 0:
            self.add_item(Button(label="⬅️ Anterior", style=discord.ButtonStyle.primary, custom_id="anterior"))
        if self.current_page < self.total_pages - 1:
            self.add_item(Button(label="Próxima ➡️", style=discord.ButtonStyle.primary, custom_id="proxima"))

        self.add_item(Button(label="✅ Confirmar Participantes", style=discord.ButtonStyle.success, custom_id="confirmar"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, custom_id="")
    async def on_button_click(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        if custom_id == "anterior":
            self.current_page -= 1
        elif custom_id == "proxima":
            self.current_page += 1
        elif custom_id == "confirmar":
            participantes = [self.guild.get_member(int(uid)) for uid in self.selected_members]
            participantes = [p for p in participantes if p]
            await self.salvar_acao(interaction, participantes)
            return
        self.render_page()
        await interaction.response.edit_message(view=self)

    async def salvar_acao(self, interaction: discord.Interaction, participantes):
        embed = discord.Embed(title=f"{self.tipo_acao} - {self.resultado}", color=discord.Color.green())
        embed.add_field(name="🏷️ Tipo da Ação", value=self.tipo_acao, inline=True)
        embed.add_field(name="🛡️ Operação", value=self.operacao, inline=True)
        embed.add_field(name="🗓️ Data e Hora", value=self.data_hora, inline=True)
        embed.add_field(name="💰 Dinheiro", value=self.dinheiro, inline=True)
        embed.add_field(name="🏆 Resultado", value=self.resultado, inline=True)

        bloco, blocos = "", []
        for p in participantes:
            if len(bloco) + len(p.mention) + 1 > 1024:
                blocos.append(bloco)
                bloco = ""
            bloco += f"{p.mention} "
        if bloco:
            blocos.append(bloco)

        for i, b in enumerate(blocos):
            embed.add_field(name=f"👥 Participantes ({i+1})", value=b.strip(), inline=False)

        participantes_str = " ".join([p.mention for p in participantes])

        conn = sqlite3.connect("relatorio.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_acao TEXT NOT NULL,
                resultado TEXT NOT NULL,
                operacao TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                dinheiro TEXT NOT NULL,
                participantes TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO acoes (tipo_acao, resultado, operacao, data_hora, dinheiro, participantes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.tipo_acao, self.resultado, self.operacao, self.data_hora, self.dinheiro, participantes_str))
        conn.commit()
        acao_id = cursor.lastrowid
        conn.close()

        logger.info(f"[DB] Ação registrada com sucesso: ID {acao_id}")

        await enviar_acao_completa(interaction, embed, participantes, acao_id)
        await interaction.response.send_message("✅ Ação registrada com sucesso!", ephemeral=True)
