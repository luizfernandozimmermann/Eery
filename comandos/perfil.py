from enum import Enum
import disnake
from disnake.ext import commands
from re import match

from entidades.EeryType import EeryType


def validar_link(link : str) -> bool:
    regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
    return match(regex, link) is not None


class Time(Enum):
    TODOS = {"nome": "Todos", "vulgo": "Todos os times"}
    REMOVER = {"nome": "Remover", "vulgo": "Remove o time do seu perfil"}
    AMERICA_MG = {"nome": "América-MG", "vulgo": "Vulgo Coelho"}
    ATHLETICO_PR = {"nome": "Athletico-PR", "vulgo": "Vulgo Furacão"}
    ATLETICO_MG = {"nome": "Atlético-MG", "vulgo": "Vulgo Galo"}
    BAHIA = {"nome": "Bahia", "vulgo": "Vulgo Esquadrão de Aço"}
    BOTAFOGO = {"nome": "Botafogo", "vulgo": "Vulgo Fogão"}
    CORINTHIANS = {"nome": "Corinthians", "vulgo": "Vulgo Timão"}
    CORITIBA = {"nome": "Coritiba", "vulgo": "Vulgo Coxa"}
    CRUZEIRO = {"nome": "Cruzeiro", "vulgo": "Vulgo Cabuloso"}
    CUIABA = {"nome": "Cuiabá", "vulgo": "Vulgo Dourado"}
    FLAMENGO = {"nome": "Flamengo", "vulgo": "Vulgo Mengão"}
    FLUMINENSE = {"nome": "Fluminense", "vulgo": "Vulgo Flu"}
    FORTALEZA = {"nome": "Fortaleza", "vulgo": "Vulgo Leão"}
    GOIAS = {"nome": "Goiás", "vulgo": "Vulgo Esmeraldino"}
    GREMIO = {"nome": "Grêmio", "vulgo": "Vulgo Tricolor Gaúcho"}
    INTERNACIONAL = {"nome": "Internacional", "vulgo": "Vulgo Inter"}
    PALMEIRAS = {"nome": "Palmeiras", "vulgo": "Vulgo Verdão"}
    RED_BULL_BRAGANTINO = {"nome": "Red Bull Bragantino", "vulgo": "Vulgo Massa Bruta"}
    SANTOS = {"nome": "Santos", "vulgo": "Vulgo Peixe"}
    SAO_PAULO = {"nome": "São Paulo", "vulgo": "Vulgo Trikas"}
    VASCO_DA_GAMA = {"nome": "Vasco da Gama", "vulgo": "Vulgo GIGANTE DA COLINA KKKKKKKKKKKKKKK"}


class Perfil(commands.Cog):
    def __init__(self, bot : EeryType):
        self.bot = bot
        self.usuario_servico = bot.usuario_servico
        
    @commands.slash_command(name="perfil", description="Mostra seu perfil")
    async def perfil(self, inter : disnake.ApplicationCommandInteraction, usuario : disnake.User = None):
        await inter.response.defer()

        usuario = self.usuario_servico.pegar_usuario_valido(inter.user, usuario)

        embed_perfil = disnake.Embed(
            title = f"Perfil de {usuario.name}",
            colour=disnake.Colour.blue()
        )
        embed_perfil.set_thumbnail(usuario.avatar)
        embed_perfil.add_field(
            name="Nick",
            value=usuario.global_name
        )
        
        for key, value in self.usuario_servico.usuario_info_para_dict(usuario).items():
            if value != None and key not in ["xp"]:
                if key == "twitch":
                    value = f"https://www.twitch.tv/{value}"

                embed_perfil.add_field(
                    name= key.replace("_", " ").title(),
                    value= f"[Clique aqui]({value})" if validar_link(str(value)) else str(value),
                )

        await inter.edit_original_message(embed=embed_perfil)
        
    @commands.slash_command(name="anv", description="Registra a data do seu aniversário no perfil")
    async def anv(self, inter : disnake.ApplicationCommandInteraction, dia : int, mes : int):
        await inter.response.defer()

        if mes < 0 > dia or mes > 12 or dia > 31:
            await inter.edit_original_message("Insira uma data válida")
            return
        
        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.aniversario = f"{dia:02}/{mes:02}"
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Aniversário registrado com sucesso!")

    @commands.slash_command(name="bruno", description="Comando para adicionar ou remover Bruno points da pessoa mencionada")
    async def bruno(self, inter : disnake.ApplicationCommandInteraction, user : disnake.User , pontos : int):
        await inter.response.defer()

        if inter.author.id not in [249674362410631169, self.bot.owner.id]:
            await inter.edit_original_message("Você não possui permissão para alterar os Bruno points.")
            return
        
        usuario = self.usuario_servico.pegar_usuario_valido(inter.user, user)
        usuario.bruno_points += int(pontos)
        self.usuario_servico.salvar_usuario(usuario)
        
        await inter.channel.send(f"Atualizado os Bruno Point de {usuario.name} em {pontos} pontos. Agora ele(a) possui {usuario.bruno_points} pontos.")

    @commands.slash_command(name="estado", description="Registra seu Estado no perfil")
    async def estado(self, inter : disnake.ApplicationCommandInteraction, estado : str):
        await inter.response.defer()
        
        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.estado = estado.strip()
        self.usuario_servico.salvar_usuario(usuario)
        
        await inter.edit_original_message("Estado registrado com sucesso!")

    @commands.slash_command(name="twitter", description="Registra sua conta no site com X no perfil")
    async def nome(self, inter : disnake.ApplicationCommandInteraction, 
                   twitter : str, tipo = commands.Param(choices=["Link", "Usuário"])):
        await inter.response.defer()
        
        twitter = twitter.strip()
        
        if tipo == "Link" and not validar_link(twitter):
            await inter.edit_original_message("Coloque um link válido.")
            return

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.twitter = twitter.strip()
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Twitter registrado com sucesso!")
        
    @commands.slash_command(name="lista_anime", description="Registra sua lista de anime (Anilist, MAL, etc.) no perfil")
    async def lista_anime(self, inter : disnake.ApplicationCommandInteraction, link : str):
        await inter.response.defer()

        link = link.strip()
        if not validar_link(link):
            await inter.edit_original_message("Coloque um link válido.")
            return

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.lista_animes = link
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Lista de animes registrada com sucesso!")
        
    @commands.slash_command(name="steam", description="Registra sua conta da Steam no perfil")
    async def steam(self, inter : disnake.ApplicationCommandInteraction, 
                    steam : str, tipo = commands.Param(choices=["Link", "Usuário"])):
        await inter.response.defer()
        
        steam = steam.strip()

        if tipo == "Link" and not validar_link(steam):
            await inter.edit_original_message("Coloque um link válido.")
            return

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.steam = steam
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Steam registrada com sucesso!")

    @commands.slash_command(name="insta", description="Registra sua conta do Instagram no perfil")
    async def insta(self, inter : disnake.ApplicationCommandInteraction, 
                    instagram : str, tipo = commands.Param(choices=["Link", "Usuário"])):
        await inter.response.defer()
        
        instagram = instagram.strip()

        if tipo == "Link" and not validar_link(instagram):
            await inter.edit_original_message("Coloque um link válido.")
            return

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.instagram = instagram
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Instagram registrado com sucesso!")
        
    @commands.slash_command(name="osu", description="Registra sua conta do Osu! no perfil")
    async def osu(self, inter : disnake.ApplicationCommandInteraction, 
                  osu : str, tipo = commands.Param(choices=["Link", "Usuário"])):
        await inter.response.defer()

        osu = osu.strip()
        if tipo == "Link" and not validar_link(osu):
            await inter.edit_original_message("Coloque um link válido.")
            return

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.osu = osu
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Osu! registrado com sucesso!")

    @commands.slash_command(name="genshin", description="Registra seu UID do Genshin no perfil")
    async def genshin(self, inter : disnake.ApplicationCommandInteraction, uid : int):
        await inter.response.defer()

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.genshin_uid = str(uid)
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Genshin UID registrado com sucesso!")

    @commands.slash_command(name="honkai", description="Registra seu UID do Honkai no perfil")
    async def honkai(self, inter : disnake.ApplicationCommandInteraction, uid : int):
        await inter.response.defer()

        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.honkai_uid = str(uid)
        self.usuario_servico.salvar_usuario(usuario)

        await inter.edit_original_message("Honkai UID registrado com sucesso!")

    @commands.slash_command(name="time", description="Adiciona seu time no perfil no perfil")
    async def time(self, inter : disnake.ApplicationCommandInteraction):
        options = [
            disnake.SelectOption(
                label=e.value["nome"], description=e.value["vulgo"]
                ) for e in Time if e.value["nome"] != "Todos"
            ]
        
        select = disnake.ui.Select(
            placeholder= "Escolha seu time!",
            options=options
        )
        
        async def selecao_callback(inter_select : disnake.MessageInteraction):
            if inter_select.user == inter.user:
                await inter_select.response.edit_message("\u3164", view=None)
                time = select.values[0]
                
                usuario = self.usuario_servico.pegar_usuario(inter_select.user)
                if time == "Remover":
                    if usuario.time == None:
                        await inter_select.edit_original_message(f"Você não possui nenhum time selecinado.")
                        return
                    
                    await inter_select.edit_original_message(
                        f"O time {usuario.time} foi removido do perfil com sucesso!")
                    
                    usuario.time = None
                    
                else:
                    usuario.time = time
                    await inter_select.edit_original_message(f"O time {time} foi selecionado para o perfil!")
                    
                self.usuario_servico.salvar_usuario(usuario)
        
        select.callback = selecao_callback
        
        view = disnake.ui.View()
        view.add_item(select)
        await inter.response.send_message(view=view)
    
    @commands.slash_command(name="arquibancada", description="Mostra os torcedores de todos os times ou do time selecionado")   
    async def arquibancada(self, inter : disnake.ApplicationCommandInteraction, 
                           time = commands.Param(choices=[e.value["nome"] for e in Time if e.value["nome"] != "Remover"])):
        await inter.response.defer()
        
        usuarios = sorted(
            filter(
                lambda usuario: usuario.time != None,
                self.usuario_servico.pegar_todos_usuarios()
                ),
            key=lambda usuario: (usuario.time, usuario.display_name)
            )
        
        times = {
            key: [usuario.id for usuario in usuarios if usuario.time == key]
            for key in [usuario.time for usuario in usuarios]
        }
        
        for time_dict, torcedores in times.items():
            for pos, torcedor in enumerate(torcedores):
                times[time_dict][pos] = f"<@{torcedor}>"
                    
        embed = disnake.Embed(
            title="Arquibancada da União Sinistra",
            colour=disnake.Colour.blue()
        )
        embed.set_footer(text="Qualquer desentendimento entre torcedores levará todos ao gulag.")
        
        if time == "Todos":
            for time_dict, torcedores in times.items():
                if torcedores != []:
                    embed.add_field(
                        name=time_dict,
                        value=", ".join(torcedores),
                        inline=False
                    )
        else:
            embed.title += f" - {time}"
            embed.description = "\n".join(times[time]) if time in times else "Time abandonado por Deus"
        
        await inter.edit_original_message(embed=embed)
    