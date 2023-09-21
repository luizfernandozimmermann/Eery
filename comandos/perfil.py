from enum import Enum
import disnake
from disnake.ext import commands
from save_and_load import *
from re import match


def validar_link(link : str) -> bool:
        regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
        return match(regex, link) is not None

def registrar(usuario : disnake.Member | disnake.User):
    membros = carregar()
        
    if str(usuario.id) in membros:
        return False

    membros[str(usuario.id)] = {
        "nick": usuario.name,
        "nome": None,
        "aniversario": None,
        "estado": None,
        "twitter": None,
        "twitch": None,
        "lista_animes": None,
        "steam": None,
        "instagram": None,
        "osu": None,
        "genshin_uid": None,
        "bruno_points": 0
    }

    salvar(membros)
    return True


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
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        
    @commands.slash_command(name="registrar", description="Registrar seu usuário de discord no perfil")
    async def registrar(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        if not registrar(inter.user):
            await inter.edit_original_message("Você já está registrado.")
            return
        await inter.edit_original_message("Registrado com sucesso!")

    @commands.slash_command(name="perfil", description="Mostra seu perfil")
    async def perfil(self, inter : disnake.ApplicationCommandInteraction, usuario : disnake.User = None):
        await inter.response.defer()

        if usuario == None:
            usuario = inter.user

        membros = carregar()

        if str(usuario.id) not in membros:
            await inter.edit_original_message(f"Usuário <@{usuario.id}> não está registrado.")
            return

        embed_perfil = disnake.Embed(
            title = f"Perfil de {usuario.name}",
            colour=disnake.Colour.blue()
        )
        embed_perfil.set_thumbnail(usuario.avatar)
        
        membro : dict[str, str] = membros[str(usuario.id)]
        
        for key, value in membro.items():
            if value != None and key not in ["xp"]:
                if key == "twitch":
                    value = f"https://www.twitch.tv/{value}"

                embed_perfil.add_field(
                    name= key.replace("_", " ").title(),
                    value= f"[Clique aqui]({value})" if validar_link(str(value)) else str(value),
                )

        await inter.edit_original_message(embed=embed_perfil)
        
    @commands.slash_command(name="nick", description="Atualiza seu nick no perfil")
    async def nick(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["nick"] = inter.author.name
        salvar(membros)
        await inter.edit_original_message("Nick atualizado com sucesso!")
        
    @commands.slash_command(name="anv", description="Registra a data do seu aniversário no perfil")
    async def anv(self, inter : disnake.ApplicationCommandInteraction, dia : int, mes : int):
        await inter.response.defer()

        if mes < 0 > dia or mes > 12 or dia > 31:
            await inter.edit_original_message("Insira uma data válida")
            return
        
        membros = carregar()
        membros[str(inter.user.id)]["aniversario"] = f"{dia:02}/{mes:02}"
        salvar(membros)

        await inter.edit_original_message("Aniversário registrado com sucesso!")

    @commands.slash_command(name="estado", description="Registra seu Estado no perfil")
    async def estado(self, inter : disnake.ApplicationCommandInteraction, estado : str):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["estado"] = estado.strip()
        await inter.edit_original_message("Estado registrado com sucesso!")
        salvar(membros)

    @commands.slash_command(name="twitter", description="Registra sua conta no site com X no perfil")
    async def nome(self, inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
        await inter.response.defer()

        if link == usuario == None:
            await inter.edit_original_message("Coloque o link para seu perfil ou o nome de seu usuário do Twitter")
            return
        
        if link != None:
            link = link.strip()
            link_valido = validar_link(link)
            if not link_valido:
                await inter.edit_original_message("Coloque um link válido.")
                return
            
            usuario = link

        membros = carregar()
        membros[str(inter.author.id)]["twitter"] = usuario.strip()
        salvar(membros)

        await inter.edit_original_message("Twitter registrado com sucesso!")
        
    @commands.slash_command(name="lista_anime", description="Registra sua lista de anime (Anilist, MAL, etc.) no perfil")
    async def lista_anime(self, inter : disnake.ApplicationCommandInteraction, link : str):
        await inter.response.defer()

        link = link.strip()
        link_valido = validar_link(link)
        if not link_valido:
            await inter.edit_original_message("Coloque um link válido.")
            return

        membros = carregar()
        membros[str(inter.author.id)]["lista_animes"] = link
        salvar(membros)

        await inter.edit_original_message("Lista de animes registrada com sucesso!")
        
    @commands.slash_command(name="steam", description="Registra sua conta da Steam no perfil")
    async def steam(self, inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
        await inter.response.defer()

        if link == usuario == None:
            await inter.edit_original_message("Coloque o link para seu perfil ou o nome de seu usuário da Steam")
            return
        
        if link != None:
            link = link.strip()
            link_valido = validar_link(link)
            if not link_valido:
                await inter.edit_original_message("Coloque um link válido.")
                return
            
            usuario = link

        membros = carregar()
        membros[str(inter.author.id)]["steam"] = usuario.strip()
        salvar(membros)

        await inter.edit_original_message("Steam registrada com sucesso!")

    @commands.slash_command(name="insta", description="Registra sua conta do Instagram no perfil")
    async def insta(self, inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
        await inter.response.defer()

        if link == usuario == None:
            await inter.edit_original_message("Coloque o link para seu perfil ou o nome de seu usuário do Instagram")
            return
        
        if link != None:
            link = link.strip()
            link_valido = validar_link(link)
            if not link_valido:
                await inter.edit_original_message("Coloque um link válido.")
                return
            
            usuario = link

        membros = carregar()
        membros[str(inter.author.id)]["instagram"] = usuario.strip()
        salvar(membros)

        await inter.edit_original_message("Instagram registrado com sucesso!")
        
    @commands.slash_command(name="osu", description="Registra sua conta do Osu! no perfil")
    async def osu(self, inter : disnake.ApplicationCommandInteraction, link : str):
        await inter.response.defer()

        link = link.strip()
        link_valido = validar_link(link)
        if not link_valido:
            await inter.edit_original_message("Coloque um link válido.")
            return

        membros = carregar()
        membros[str(inter.author.id)]["osu"] = link
        salvar(membros)

        await inter.edit_original_message("Osu! registrado com sucesso!")

    @commands.slash_command(name="genshin", description="Registra seu UID do Genshin no perfil")
    async def genshin(self, inter : disnake.ApplicationCommandInteraction, uid : str):
        await inter.response.defer()

        membros = carregar()
        membros[str(inter.author.id)]["genshin_uid"] = uid
        salvar(membros)

        await inter.edit_original_message("Genshin UID registrado com sucesso!")

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
                
                membros = carregar()
                if time == "Remover":
                    time_registrado = membros[str(inter_select.user.id)]["time"]
                    if time_registrado == None:
                        await inter_select.edit_original_message(f"Você não possui nenhum time selecinado.")
                        return
                    
                    membros[str(inter_select.user.id)]["time"] = None
                    salvar(membros)
                    await inter_select.edit_original_message(
                        f"O time {time_registrado} foi removido do perfil com sucesso!")
                    return
                
                membros[str(inter_select.user.id)]["time"] = time
                salvar(membros)
                await inter_select.edit_original_message(f"O time {time} foi selecionado para o perfil!")
        
        select.callback = selecao_callback
        
        view = disnake.ui.View()
        view.add_item(select)
        await inter.response.send_message(view=view)
    
    @commands.slash_command(name="arquibancada", description="Mostra os torcedores de todos os times ou do time selecionado")   
    async def arquibancada(self, inter : disnake.ApplicationCommandInteraction, 
                           time = commands.Param(choices=[e.value["nome"] for e in Time if e.value["nome"] != "Remover"])):
        await inter.response.defer()
        
        membros = carregar()
        
        times = {}
        for id, info in membros.items():
            if info["time"] != None:
                if info["time"] not in times:
                    times[info["time"]] = []
                times[info["time"]].append(self.bot.get_user(int(id)))
        
        times = dict(sorted(times.items()))
        
        for time_dict, torcedores in times.items():
            if torcedores != []:
                torcedores = sorted(torcedores, key=lambda x: x.display_name)
                
                for pos, torcedor in enumerate(torcedores):
                    times[time_dict][pos] = f"<@{torcedor.id}>"
                    
        embed = disnake.Embed(
            title="Arquibancada da União Sinistra",
            colour=disnake.Colour.blurple()
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
    
   
def setup(bot: commands.Bot):
    bot.add_cog(Perfil(bot))
