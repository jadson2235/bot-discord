import discord
from discord.ext import commands
from discord import ui, ButtonStyle
import json
import os
from datetime import datetime

# ============================================
# CONFIGURAÇÃO
# ============================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

REGISTROS_FILE = "registros.json"

# ============================================
# FUNÇÕES
# ============================================
def carregar_registros():
    if os.path.exists(REGISTROS_FILE):
        with open(REGISTROS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_registro(user_id, dados):
    registros = carregar_registros()
    registros[str(user_id)] = dados
    with open(REGISTROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

# ============================================
# MODAL
# ============================================
class RegistroModal(ui.Modal, title="Registro"):

    nome = ui.TextInput(label="Nome completo")
    id_membro = ui.TextInput(label="ID do membro")
    idade = ui.TextInput(label="Idade")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            idade = int(self.idade.value)
        except:
            await interaction.response.send_message("Idade inválida!", ephemeral=True)
            return

        salvar_registro(interaction.user.id, {
            "nome": self.nome.value,
            "id_membro": self.id_membro.value,
            "idade": idade,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

        await interaction.response.send_message("✅ Registrado com sucesso!", ephemeral=True)

# ============================================
# BOTÕES
# ============================================
class BotoesRegistro(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Registrar", style=ButtonStyle.green)
    async def registrar(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RegistroModal())

# ============================================
# COMANDO
# ============================================
@bot.command()
async def registro(ctx):
    embed = discord.Embed(
        title="Registro",
        description="Clique no botão para se registrar",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=BotoesRegistro())

# ============================================
# EVENTO
# ============================================
@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")

# ============================================
# INICIAR BOT (CORRIGIDO PARA RENDER)
# ============================================
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")

    if not TOKEN:
        print("❌ TOKEN não encontrado!")
    else:
        bot.run(TOKEN)
