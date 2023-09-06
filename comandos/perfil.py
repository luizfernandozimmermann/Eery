import disnake
from disnake.ext import commands
from save_and_load import *
from re import match


def validar_link(link : str) -> bool:
        regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
        return match(regex, link) is not None


class Perfil(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client
        
    @commands.slash_command(name="registrar", description="Registrar seu usuário de discord")
    async def registrar(inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        membros = carregar()
        
        if str(inter.author.id) in membros:
            await inter.edit_original_message("Você já está registrado.")
            return

        membros[str(inter.author.id)] = {
            "nick": inter.author.name,
            "nome": "Não informado",
            "aniversario": "Não informado",
            "estado": "Não informado",
            "twitter": "Não informado",
            "twitch": "Não informado",
            "lista_animes": "Não informado",
            "steam": "Não informado",
            "instagram": "Não informado",
            "osu": "Não informado",
            "genshin_uid": "Não informado",
            "bruno_points": 0
        }

        salvar(membros)
        await inter.edit_original_message("Registrado com sucesso!")

    @commands.slash_command(name="perfil", description="Mostra seu perfil")
    async def perfil(inter : disnake.ApplicationCommandInteraction, usuario : disnake.User = None):
        await inter.response.defer()

        usuario_id = inter.user.id
        usuario_nick = inter.user.global_name
        if usuario != None:
            usuario_id = usuario.id
            usuario_nick = usuario.global_name
        usuario_id = str(usuario_id)

        embed_perfil = disnake.Embed(
            title=usuario_nick,
            colour=disnake.Colour.blue()
        )

        membros = carregar()

        if usuario_id not in membros:
            await inter.edit_original_message(f"Usuário <@{usuario_id}> não está registrado.")
            return
        
        membro = membros[usuario_id]

        embed_perfil.description = f"""
            Nome: {membro["nome"]}
            Aniversário: {membro["aniversario"]}
            Estado: {membro["estado"]}
            Twitter: {membro["twitter"]}
            Lista de animes: {membro["lista_animes"]}
            Steam: {membro["steam"]}
            Twitch: {f"https://www.twitch.tv/{membro['twitch']}" if membro['twitch'] != "Não informado" else membro['twitch']}
            Instagram: {membro["instagram"]}
            Osu!: {membro["osu"]}
            Genshin UID: {membro["genshin_uid"]}
            Bruno points: {membro["bruno_points"]}
        """

        await inter.edit_original_message(embed=embed_perfil)
        
    @commands.slash_command(name="nick", description="Atualiza seu nick")
    async def nick(inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["nick"] = inter.author.name
        salvar(membros)
        await inter.edit_original_message("Nick atualizado com sucesso!")
        
    @commands.slash_command(name="anv", description="Registre a data do seu aniversário")
    async def anv(inter : disnake.ApplicationCommandInteraction, dia : int, mes : int):
        await inter.response.defer()

        if mes < 0 > dia or mes > 12 or dia > 31:
            await inter.edit_original_message("Insira uma data válida")
            return
        
        membros = carregar()
        membros[str(inter.user.id)]["aniversario"] = f"{dia:02}/{mes:02}"
        salvar(membros)

        await inter.edit_original_message("Aniversário registrado com sucesso!")

    @commands.slash_command(name="estado", description="Registre seu Estado")
    async def estado(inter : disnake.ApplicationCommandInteraction, estado : str):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["estado"] = estado.strip()
        await inter.edit_original_message("Estado registrado com sucesso!")
        salvar(membros)

    @commands.slash_command(name="twitter", description="Registra sua conta no site com X")
    async def nome(inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
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
        
    @commands.slash_command(name="lista_anime", description="Registra sua lista de anime (Anilist, MAL, etc.)")
    async def lista_anime(inter : disnake.ApplicationCommandInteraction, link : str):
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
        
    @commands.slash_command(name="steam", description="Registra sua conta da Steam")
    async def steam(inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
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

    @commands.slash_command(name="insta", description="Registra sua conta do Instagram")
    async def insta(inter : disnake.ApplicationCommandInteraction, link : str = None, usuario : str = None):
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
        
    @commands.slash_command(name="osu", description="Registra sua conta do Osu!")
    async def osu(inter : disnake.ApplicationCommandInteraction, link : str):
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

    @commands.slash_command(name="genshin", description="Registra seu UID do Genshin")
    async def genshin(inter : disnake.ApplicationCommandInteraction, uid : str):
        await inter.response.defer()

        membros = carregar()
        membros[str(inter.author.id)]["genshin_uid"] = uid
        salvar(membros)

        await inter.edit_original_message("Genshin UID registrado com sucesso!")

   
def setup(client: commands.Bot):
    client.add_cog(Perfil(client))
