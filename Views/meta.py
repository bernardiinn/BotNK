# Views/meta.py
import discord
import sqlite3
from datetime import datetime, timedelta

VALOR_META_SEMANAL = 70000

def get_inicio_semana():
    hoje = datetime.now()
    return hoje - timedelta(days=hoje.weekday())

def get_total_farmado(membro_id):
    inicio = get_inicio_semana().strftime("%Y-%m-%d")
    conn = sqlite3.connect('relatorio.db')
    c = conn.cursor()
    c.execute("""
        SELECT SUM(valor) FROM farm_droga
        WHERE membro_id = ? AND data >= ?
    """, (membro_id, inicio))
    resultado = c.fetchone()
    conn.close()
    return resultado[0] or 0

def registrar_farm(membro_id, valor):
    hoje = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('relatorio.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO farm_droga (membro_id, valor, data)
        VALUES (?, ?, ?)
    """, (membro_id, valor, hoje))
    conn.commit()
    conn.close()

def gerar_embed(membro_id, membro_nome):
    total = get_total_farmado(membro_id)
    restante = max(0, VALOR_META_SEMANAL - total)
    extra = max(0, total - VALOR_META_SEMANAL)

    embed = discord.Embed(title=f"📦 Progresso de Meta Semanal - {membro_nome}", color=discord.Color.green())
    embed.add_field(name="💰 Total Farmado", value=f"{total:,}K".replace(",", "."), inline=False)
    embed.add_field(name="🎯 Meta", value=f"{VALOR_META_SEMANAL:,}K".replace(",", "."), inline=True)
    embed.add_field(name="📉 Restante", value=f"{restante:,}K".replace(",", "."), inline=True)
    if extra > 0:
        embed.add_field(name="🤑 Dinheiro Extra", value=f"{extra:,}K".replace(",", "."), inline=False)

    embed.set_footer(text="Meta resetada automaticamente todo domingo.")
    return embed

class MetaModal(discord.ui.Modal, title="Adicionar Farm de Droga"):
    def __init__(self, membro_id, membro_nome, mensagem):
        super().__init__()
        self.membro_id = membro_id
        self.membro_nome = membro_nome
        self.mensagem = mensagem
        self.valor = discord.ui.TextInput(label="Quantidade em K", placeholder="Ex: 21689", required=True)
        self.add_item(self.valor)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.valor.value)
        except ValueError:
            await interaction.response.send_message("❌ Valor inválido. Digite apenas números inteiros.", ephemeral=True)
            return

        registrar_farm(self.membro_id, valor)
        embed = gerar_embed(self.membro_id, self.membro_nome)
        await self.mensagem.edit(embed=embed, view=MetaView(self.membro_id, self.membro_nome, self.mensagem))
        await interaction.response.send_message("✅ Farm registrado!", ephemeral=True)

class MetaView(discord.ui.View):
    def __init__(self, membro_id, membro_nome, mensagem):
        super().__init__(timeout=None)
        self.membro_id = membro_id
        self.membro_nome = membro_nome
        self.mensagem = mensagem

    @discord.ui.button(label="➕ Adicionar Farm", style=discord.ButtonStyle.primary)
    async def add_farm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.membro_id:
            await interaction.response.send_message("❌ Você só pode registrar sua própria meta.", ephemeral=True)
            return

        await interaction.response.send_modal(MetaModal(self.membro_id, self.membro_nome, self.mensagem))
