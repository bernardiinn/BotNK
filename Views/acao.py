import discord
import sqlite3
from datetime import datetime
from discord.ext import commands
from Views.kills import AdicionarKillsPorBotaoView, salvar_kill_callback

ID_CANAL_ACOES = None  # Será definido via injeção no setup()

TIPOS_ACAO = [
    "Banco Central", "Banco Paleto", "Banco Fleeca", "Carro Forte",
    "Joalheria", "Loja de Armas", "Loja de Departamento", "Distribuidora de Bebidas",
    "Fuga", "Tiro"
]
RESULTADOS = ["Vitória", "Vitória Parcial", "Derrota"]

# --- COMPONENTES (Views) ---

class EditarAcaoModal(discord.ui.Modal, title="Editar Ação"):
    def __init__(self, mensagem, tipo_acao, resultado, operacao, data_hora, dinheiro, participantes):
        super().__init__()
        self.mensagem = mensagem
        self.tipo_acao = tipo_acao
        self.resultado = resultado
        self.operacao = operacao
        self.participantes = participantes

        self.data_hora = discord.ui.TextInput(label="Data e Hora", default=data_hora)
        self.dinheiro = discord.ui.TextInput(label="Dinheiro Ganho", default=dinheiro)

        self.add_item(self.data_hora)
        self.add_item(self.dinheiro)

    async def on_submit(self, interaction: discord.Interaction):
        # Validar e formatar a data/hora
        try:
            partes = self.data_hora.value.split(" -")
            data_raw = partes[0] + " - " + partes[1]  # remove timezone extra se houver
            dt = datetime.strptime(data_raw.strip(), "%d/%m/%Y - %H:%M")
            data_formatada = dt.strftime("%d/%m/%Y - %H:%M")
        except Exception as e:
            await interaction.response.send_message(f"❌ Data e hora inválida: {e}", ephemeral=True)
            return

        # Validar e formatar o dinheiro
        try:
            dinheiro_formatado = f"R$ {int(self.dinheiro.value):,}".replace(",", ".")
        except ValueError:
            await interaction.response.send_message("❌ Dinheiro inválido.", ephemeral=True)
            return

        # Definir cor do embed
        if self.operacao.lower() == "fuga":
            cor = discord.Color.orange()
        elif self.operacao.lower() == "tiro":
            cor = discord.Color.red()
        else:
            cor = discord.Color.blue()

        embed = discord.Embed(title=f"{self.tipo_acao} - {self.resultado}", color=cor)
        embed.add_field(name="🏷️ Tipo da Ação", value=self.tipo_acao, inline=True)
        embed.add_field(name="🛡️ Operação", value=self.operacao, inline=True)
        embed.add_field(name="🗓️ Data e Hora", value=data_formatada, inline=True)
        embed.add_field(name="💰 Dinheiro", value=dinheiro_formatado, inline=True)
        embed.add_field(name="🏆 Resultado", value=self.resultado, inline=True)

        participantes_lista = self.participantes.split()
        bloco, blocos = "", []
        for p in participantes_lista:
            if len(bloco) + len(p) + 1 > 1024:
                blocos.append(bloco)
                bloco = ""
            bloco += f"{p} "
        if bloco:
            blocos.append(bloco)

        for i, b in enumerate(blocos):
            embed.add_field(name=f"👥 Participantes ({i+1})", value=b.strip(), inline=False)

        embed.set_footer(text=f"Editado por {interaction.user.display_name}")
        await self.mensagem.edit(embed=embed, view=EditarAcaoButton(0))
        await interaction.response.send_message("✅ Ação editada!", ephemeral=True)


class EditarAcaoButton(discord.ui.View):
    def __init__(self, acao_id):
        super().__init__(timeout=None)
        self.acao_id = acao_id

    @discord.ui.button(label="✏️ Editar Ação", style=discord.ButtonStyle.primary)
    async def editar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        mensagem = interaction.message
        embed = mensagem.embeds[0]

        tipo_acao = embed.fields[0].value
        operacao = embed.fields[1].value
        data_hora = embed.fields[2].value
        dinheiro = embed.fields[3].value.replace("R$ ", "").replace(".", "")
        resultado = embed.fields[4].value
        participantes = " ".join(field.value for field in embed.fields if field.name.startswith("👥"))

        await interaction.response.send_modal(
            EditarAcaoModal(mensagem, tipo_acao, resultado, operacao, data_hora, dinheiro, participantes)
        )

    @discord.ui.button(label="💥 Registrar Kills", style=discord.ButtonStyle.danger)
    async def kills_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        mensagem = interaction.message
        embed = mensagem.embeds[0]
        participantes_ment = " ".join(field.value for field in embed.fields if field.name.startswith("👥"))
        participantes = [interaction.guild.get_member(int(p[2:-1])) for p in participantes_ment.split() if p.startswith("<@") and p.endswith(">")]
        participantes = [p for p in participantes if p is not None]

        await interaction.response.send_message(
            content="Selecione um jogador para registrar kills:",
            view=AdicionarKillsPorBotaoView(participantes, self.acao_id, salvar_kill_callback),
            ephemeral=True
        )


class EscolhaInicial(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.tipo_acao = None
        self.resultado = None
        self.operacao = None

        self.tipo_select = discord.ui.Select(
            placeholder="Escolha o Tipo de Ação",
            options=[discord.SelectOption(label=tipo) for tipo in TIPOS_ACAO],
            custom_id="select_tipo_acao"
        )
        self.tipo_select.callback = self.set_tipo

        self.resultado_select = discord.ui.Select(
            placeholder="Escolha o Resultado",
            options=[discord.SelectOption(label=res) for res in RESULTADOS],
            custom_id="select_resultado"
        )
        self.resultado_select.callback = self.set_resultado

        self.operacao_select = discord.ui.Select(
            placeholder="Escolha a Operação",
            options=[discord.SelectOption(label=o) for o in ["Fuga", "Tiro"]],
            custom_id="select_operacao"
        )
        self.operacao_select.callback = self.set_operacao

        self.confirmar_button = discord.ui.Button(
            label="Confirmar",
            style=discord.ButtonStyle.success,
            custom_id="botao_confirmar_acao"
        )
        self.confirmar_button.callback = self.confirmar

        self.add_item(self.tipo_select)
        self.add_item(self.resultado_select)
        self.add_item(self.operacao_select)
        self.add_item(self.confirmar_button)

    async def set_tipo(self, interaction: discord.Interaction):
        self.tipo_acao = self.tipo_select.values[0]
        await interaction.response.defer()

    async def set_resultado(self, interaction: discord.Interaction):
        self.resultado = self.resultado_select.values[0]
        await interaction.response.defer()

    async def set_operacao(self, interaction: discord.Interaction):
        self.operacao = self.operacao_select.values[0]
        await interaction.response.defer()

    async def confirmar(self, interaction: discord.Interaction):
        if not all([self.tipo_acao, self.resultado, self.operacao]):
            await interaction.response.send_message("Selecione todos os campos.", ephemeral=True)
            return

        await interaction.response.send_modal(ActionModal(self.tipo_acao, self.resultado, self.operacao))

class ActionModal(discord.ui.Modal, title="Registrar Ação"):
    def __init__(self, tipo_acao, resultado, operacao):
        super().__init__()
        self.tipo_acao = tipo_acao
        self.resultado = resultado
        self.operacao = operacao

        now = datetime.now().strftime("%d/%m/%Y - %H:%M")
        self.data_hora = discord.ui.TextInput(label="Data e Hora", default=now, required=True)
        self.dinheiro = discord.ui.TextInput(label="Dinheiro Ganho", placeholder="Ex: 250000", required=True)

        self.add_item(self.data_hora)
        self.add_item(self.dinheiro)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            partes = self.data_hora.value.split(" -")
            data_raw = partes[0] + " - " + partes[1]
            dt = datetime.strptime(data_raw.strip(), "%d/%m/%Y - %H:%M")
            data_formatada = dt.strftime("%d/%m/%Y - %H:%M")
        except Exception as e:
            await interaction.response.send_message(f"❌ Data e hora inválida: {e}", ephemeral=True)
            return

        try:
            dinheiro_formatado = f"R$ {int(self.dinheiro.value):,}".replace(",", ".")
        except ValueError:
            await interaction.response.send_message("❌ Dinheiro inválido.", ephemeral=True)
            return

        if self.operacao.lower() == "fuga":
            cor = discord.Color.orange()
        elif self.operacao.lower() == "tiro":
            cor = discord.Color.red()
        else:
            cor = discord.Color.blue()

        embed = discord.Embed(title=f"{self.tipo_acao} - {self.resultado}", color=cor)
        embed.add_field(name="🏷️ Tipo da Ação", value=self.tipo_acao, inline=True)
        embed.add_field(name="🛡️ Operação", value=self.operacao, inline=True)
        embed.add_field(name="🗓️ Data e Hora", value=data_formatada, inline=True)
        embed.add_field(name="💰 Dinheiro", value=dinheiro_formatado, inline=True)
        embed.add_field(name="🏆 Resultado", value=self.resultado, inline=True)

        await enviar_acao_completa(interaction, embed, [], acao_id=0)
        await interaction.response.send_message("✅ Ação registrada com sucesso.", ephemeral=True)


async def enviar_acao_completa(interaction: discord.Interaction, embed: discord.Embed, participantes: list, acao_id: int):
    canal = interaction.guild.get_channel(ID_CANAL_ACOES)
    await canal.send(embed=embed, view=EditarAcaoButton(acao_id))


def setup_views(bot: commands.Bot, canal_acoes_id: int):
    global ID_CANAL_ACOES
    ID_CANAL_ACOES = canal_acoes_id
    bot.add_view(EscolhaInicial())
