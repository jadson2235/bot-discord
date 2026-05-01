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

# SEM IMAGEM POR ENQUANTO (DEPOIS VOCÊ ADICIONA)
IMAGEM_VERTICAL_URL = None

# ARQUIVO DE REGISTROS
REGISTROS_FILE = "registros.json"

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
# MODAL DE REGISTRO
# ============================================
class RegistroModal(ui.Modal, title="📝 FORMULÁRIO DE REGISTRO"):
    
    def __init__(self):
        super().__init__(timeout=300)
        
        self.nome = ui.TextInput(
            label="NOME COMPLETO",
            placeholder="Digite seu nome completo",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.nome)
        
        self.id_membro = ui.TextInput(
            label="ID DO MEMBRO",
            placeholder="Ex: JOÃO123 ou MEMBRO-001",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.id_membro)
        
        self.idade = ui.TextInput(
            label="IDADE",
            placeholder="Digite apenas números",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.idade)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Validar idade
        try:
            idade_num = int(self.idade.value)
            if idade_num < 13:
                await interaction.response.send_message("❌ Você precisa ter pelo menos 13 anos!", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ Idade inválida! Digite apenas números.", ephemeral=True)
            return
        
        # Verificar se ID já existe
        registros = carregar_registros()
        for dados in registros.values():
            if dados.get('id_membro') == self.id_membro.value:
                await interaction.response.send_message(f"❌ O ID `{self.id_membro.value}` já está em uso!", ephemeral=True)
                return
        
        # Verificar se já está registrado
        if str(interaction.user.id) in registros:
            await interaction.response.send_message("❌ Você já está registrado!", ephemeral=True)
            return
        
        # Salvar registro
        salvar_registro(interaction.user.id, {
            "nome": self.nome.value,
            "id_membro": self.id_membro.value,
            "idade": self.idade.value,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        
        # Dar cargo
        cargo = discord.utils.get(interaction.guild.roles, name="Registrado")
        if cargo:
            await interaction.user.add_roles(cargo)
        
        # Mensagem de sucesso
        embed = discord.Embed(
            title="✅ REGISTRO CONCLUÍDO!",
            description=f"**{self.nome.value}**, seja bem-vindo(a) ao servidor!",
            color=discord.Color.green()
        )
        embed.add_field(name="📛 NOME", value=self.nome.value, inline=False)
        embed.add_field(name="🆔 ID DO MEMBRO", value=self.id_membro.value, inline=False)
        embed.add_field(name="🎂 IDADE", value=f"{self.idade.value} anos", inline=False)
        embed.set_footer(text=f"Registrado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        
        # Avisar admins (opcional)
        canal_admin = discord.utils.get(interaction.guild.text_channels, name="admins")
        if canal_admin:
            await canal_admin.send(f"📝 Novo registro: {self.nome.value} ({self.id_membro.value})")

# ============================================
# BOTÕES DA MENSAGEM
# ============================================
class BotoesRegistro(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="📝 REGISTRAR", style=ButtonStyle.success, emoji="✅")
    async def registrar(self, interaction: discord.Interaction, button: ui.Button):
        registros = carregar_registros()
        if str(interaction.user.id) in registros:
            await interaction.response.send_message("❌ Você já está registrado!", ephemeral=True)
            return
        
        modal = RegistroModal()
        await interaction.response.send_modal(modal)
    
    @ui.button(label="🔍 VERIFICAR", style=ButtonStyle.secondary, emoji="🔍")
    async def verificar(self, interaction: discord.Interaction, button: ui.Button):
        registros = carregar_registros()
        dados = registros.get(str(interaction.user.id))
        
        if dados:
            embed = discord.Embed(
                title="✅ VOCÊ ESTÁ REGISTRADO!",
                color=discord.Color.green()
            )
            embed.add_field(name="📛 Nome", value=dados['nome'], inline=False)
            embed.add_field(name="🆔 ID", value=dados['id_membro'], inline=False)
            embed.add_field(name="🎂 Idade", value=f"{dados['idade']} anos", inline=False)
            embed.add_field(name="📅 Data", value=dados['data'], inline=False)
        else:
            embed = discord.Embed(
                title="❌ VOCÊ NÃO ESTÁ REGISTRADO!",
                description="Clique no botão **REGISTRAR** para se cadastrar.",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="📜 REGRAS", style=ButtonStyle.primary, emoji="📖")
    async def regras(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="📜 REGRAS DO SERVIDOR",
            description="""
**1️⃣ RESPEITO** - Trate todos os membros com respeito
**2️⃣ SEM SPAM** - Não envie mensagens repetitivas
**3️⃣ CONTEÚDO APROPRIADO** - Proibido conteúdo NSFW
**4️⃣ SEM DIVULGAÇÃO** - Não divulgue outros servidores
**5️⃣ REGISTRO OBRIGATÓRIO** - Todos devem se registrar
            """,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Registre-se usando o botão verde acima")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================
# COMANDOS
# ============================================
@bot.command(name='registro')
@commands.has_permissions(administrator=True)
async def cmd_registro(ctx, canal: discord.TextChannel = None):
    """!registro #canal - Envia a mensagem de registro"""
    
    canal_alvo = canal or ctx.channel
    
    # Criar embed
    embed = discord.Embed(
        title="🎉 SISTEMA DE REGISTRO",
        description="""
**👋 OLÁ, NOVO MEMBRO!**

Antes de acessar o servidor, você precisa se registrar.

───────────────────
**📝 COMO SE REGISTRAR:**

**1.** Clique no botão **REGISTRAR**
**2.** Preencha o formulário com:
   • NOME completo
   • ID do membro
   • IDADE
**3.** Envie e aguarde confirmação

───────────────────
**✨ APÓS REGISTRAR:**

✅ Acesso a todos os canais
✅ Cargo especial de membro
✅ Participar de eventos

───────────────────
**⚠️ IMPORTANTE:**

• Apenas UM registro por pessoa
• ID único no servidor
• Idade mínima: 13 anos
""",
        color=discord.Color.purple()
    )
    
    # Adicionar imagem se tiver
    if IMAGEM_VERTICAL_URL:
        embed.set_image(url=IMAGEM_VERTICAL_URL)
    
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text="🔒 Clique no botão verde abaixo para começar")
    
    view = BotoesRegistro()
    
    await canal_alvo.send(embed=embed, view=view)
    await ctx.send(f"✅ Mensagem de registro enviada em {canal_alvo.mention}!")

@bot.command(name='listar')
@commands.has_permissions(administrator=True)
async def cmd_listar(ctx):
    """!listar - Lista todos os membros registrados"""
    
    registros = carregar_registros()
    
    if not registros:
        await ctx.send("📭 Nenhum registro encontrado ainda!")
        return
    
    embed = discord.Embed(
        title="📋 MEMBROS REGISTRADOS",
        color=discord.Color.blue()
    )
    
    descricao = ""
    for user_id, dados in registros.items():
        membro = ctx.guild.get_member(int(user_id))
        nome_membro = membro.name if membro else "Usuário saiu"
        descricao += f"**{dados['id_membro']}** - {dados['nome']} ({dados['idade']} anos) - {nome_membro}\n"
        
        if len(descricao) > 1000:
            embed.description = descricao
            await ctx.send(embed=embed)
            descricao = ""
            embed = discord.Embed(color=discord.Color.blue())
    
    if descricao:
        embed.description = descricao
        await ctx.send(embed=embed)
    
    await ctx.send(f"📊 **Total:** {len(registros)} membros registrados")

@bot.command(name='buscar')
@commands.has_permissions(administrator=True)
async def cmd_buscar(ctx, *, id_membro: str):
    """!buscar ID - Busca um registro pelo ID"""
    
    registros = carregar_registros()
    
    for user_id, dados in registros.items():
        if dados['id_membro'].lower() == id_membro.lower():
            membro = ctx.guild.get_member(int(user_id))
            embed = discord.Embed(
                title="🔍 REGISTRO ENCONTRADO",
                color=discord.Color.green()
            )
            embed.add_field(name="📛 Nome", value=dados['nome'], inline=False)
            embed.add_field(name="🆔 ID do Membro", value=dados['id_membro'], inline=False)
            embed.add_field(name="🎂 Idade", value=f"{dados['idade']} anos", inline=False)
            embed.add_field(name="👤 Usuário Discord", value=membro.mention if membro else "Não está mais no servidor", inline=False)
            embed.add_field(name="📅 Data do Registro", value=dados['data'], inline=False)
            await ctx.send(embed=embed)
            return
    
    await ctx.send(f"❌ Nenhum registro encontrado com o ID: `{id_membro}`")

@bot.command(name='remover')
@commands.has_permissions(administrator=True)
async def cmd_remover(ctx, membro: discord.Member):
    """!remover @usuario - Remove o registro de um membro"""
    
    registros = carregar_registros()
    
    if str(membro.id) in registros:
        del registros[str(membro.id)]
        with open(REGISTROS_FILE, 'w', encoding='utf-8') as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        
        # Remover cargo
        cargo = discord.utils.get(ctx.guild.roles, name="Registrado")
        if cargo and cargo in membro.roles:
            await membro.remove_roles(cargo)
        
        await ctx.send(f"✅ Registro de {membro.mention} removido com sucesso!")
    else:
        await ctx.send(f"❌ {membro.mention} não está registrado!")

@bot.command(name='stats')
@commands.has_permissions(administrator=True)
async def cmd_stats(ctx):
    """!stats - Mostra estatísticas do sistema"""
    
    registros = carregar_registros()
    
    embed = discord.Embed(
        title="📊 ESTATÍSTICAS DO SISTEMA",
        color=discord.Color.gold()
    )
    embed.add_field(name="📝 Total de registros", value=str(len(registros)), inline=True)
    embed.add_field(name="🎂 Média de idade", value="Calculando...", inline=True)
    embed.add_field(name="✅ Status", value="Ativo", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ajuda')
async def cmd_ajuda(ctx):
    """!ajuda - Mostra todos os comandos"""
    
    embed = discord.Embed(
        title="🤖 BOT DE REGISTRO - MANUAL DE COMANDOS",
        description="**Comandos disponíveis:**",
        color=discord.Color.blue()
    )
    embed.add_field(name="📤 `!registro #canal`", value="Envia a mensagem de registro no canal especificado", inline=False)
    embed.add_field(name="📋 `!listar`", value="Lista todos os membros registrados", inline=False)
    embed.add_field(name="🔍 `!buscar ID`", value="Busca um registro pelo ID do membro", inline=False)
    embed.add_field(name="🗑️ `!remover @user`", value="Remove o registro de um membro", inline=False)
    embed.add_field(name="📊 `!stats`", value="Mostra estatísticas do sistema", inline=False)
    embed.add_field(name="❓ `!ajuda`", value="Mostra esta mensagem de ajuda", inline=False)
    
    embed.set_footer(text="⚠️ Comandos de gerenciamento apenas para ADMINISTRADORES")
    await ctx.send(embed=embed)

# ============================================
# EVENTOS
# ============================================
@bot.event
async def on_ready():
    print("="*50)
    print(f"✅ BOT ONLINE: {bot.user.name}")
    print(f"📡 Servidores conectados: {len(bot.guilds)}")
    print("="*50)
    print("\n📝 COMANDOS DISPONÍVEIS:")
    print("   !registro #canal - Criar mensagem de registro")
    print("   !listar - Listar registrados")
    print("   !buscar ID - Buscar por ID")
    print("   !remover @user - Remover registro")
    print("   !stats - Estatísticas")
    print("   !ajuda - Ajuda")
    print("="*50)
    print("\n🎯 COMO USAR:")
    print("1. Digite: !registro #canal-de-registro")
    print("2. O bot enviará a mensagem com botões")
    print("3. Membros clicam em REGISTRAR")
    print("="*50)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você precisa ser **ADMINISTRADOR** para usar este comando!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Argumento faltando! Use `!ajuda` para ver como usar os comandos.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumento inválido! Use `!ajuda` para ver os exemplos.")
    else:
        await ctx.send(f"❌ Erro: {str(error)}")
        print(f"Erro detalhado: {error}")

@bot.event
async def on_member_join(member):
    """Mensagem de boas-vindas para novos membros"""
    try:
        embed = discord.Embed(
            title=f"🎉 Bem-vindo(a) ao {member.guild.name}!",
            description=f"Olá {member.mention}! 👋\n\n"
                       f"**Antes de acessar o servidor, você precisa se registrar.**\n\n"
                       f"📝 Use o comando `!registro` no canal de registro ou clique no botão **REGISTRAR**.\n\n"
                       f"**Campos necessários:**\n"
                       f"• NOME completo\n"
                       f"• ID do membro (único)\n"
                       f"• IDADE (mínimo 13 anos)",
            color=discord.Color.gold()
        )
        await member.send(embed=embed)
    except:
        pass  # Se o DM estiver fechado, ignora

import os
TOKEN = os.getenv("TOKEN")
