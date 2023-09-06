import asyncio
import json
import re
import disnake
from disnake.ext import commands
import requests

from save_and_load import *


class Comandos(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client
    
    @commands.command(name="backup")
    async def backup(self, context : commands.Context):
        if context.author.id == self.client.owner.id:
            with open("saving.json", "r") as f:
                file = disnake.File(f)
                await context.author.send(file=file)
                
    @commands.command(name="backdown")
    async def backdown(self, context : commands.Context):
        if context.author.id == self.client.owner.id:
            content = json.loads(
                requests.get(context.message.attachments[0].url, allow_redirects=True).content.decode("utf-8")
                )
            salvar(content)

    @commands.command(name="modificar")
    async def modificar(self, inter : commands.Context):
        if inter.author.id == self.client.owner.id:
            membros = carregar()
            for id, conteudo in membros.items():
                membro = membros[id]
                membro["animes"] = {}
                membros[id] = membro
            salvar(membros)
            await inter.channel.send("belezinha")


    @commands.slash_command(name="ans", description="Mostra a lista de aniversariantes, podendo escolher o mês")
    async def ans(self, inter : disnake.ApplicationCommandInteraction, mes : int = None):
        await inter.response.defer()
        embed = disnake.Embed(colour=disnake.Color.blue(), title="Aniversariantes", description="")

        membros : dict = carregar()

        membros = dict(filter(lambda item: len(item[1]["aniversario"]) == 5, membros.items()))

        if mes != None:
            if 0 > mes or mes > 12:
                await inter.edit_original_message(f"{mes} não é um mês válido.")
                return

            meses = [
                "Janeiro", "Fevereiro", "Março", "Abril", 
                "Maio", "Junho", "Julho", "Agosto", 
                "Setembro", "Outubro", "Novembro", "Dezembro"]

            membros = dict(filter(lambda item: int(item[1]["aniversario"][3:]) == mes, membros.items()))
            embed.title += f" do mês {meses[mes - 1]}"

        aniversariantes = dict(sorted(
            membros.items(), key=lambda item: (item[1]['aniversario'][3:], item[1]['aniversario'][0:2])
            ))

        for key, value in aniversariantes.items():
            embed.description += f"\n<@{key}>: {value['aniversario']}"
        
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(name="bruno", description="Comando para adicionar ou remover Bruno points da pessoa mencionada")
    async def bruno(self, inter : disnake.ApplicationCommandInteraction, usuario : disnake.User , pontos : int):
        await inter.response.defer()

        if inter.author.id not in [249674362410631169, self.client.owner.id]:
            await inter.edit_original_message("Você não possui permissão para alterar os Bruno points.")
            return
        
        membros = carregar()
        membros[str(usuario.id)]["bruno_points"] += int(pontos)
        salvar(membros)
        await inter.channel.send(f"Atualizado os Bruno Point de {usuario.name} em {pontos} pontos.")

    @commands.slash_command(name="adm", description="Comando para manutenção do bot, apenas o desenvolvedor pode utilizar")
    async def adm(self, inter : disnake.ApplicationCommandInteraction, comando : str, assincrono : bool = True):
        if inter.author.id in [self.client.owner.id, inter.guild.owner.id]:
            if not assincrono:
                exec(comando)
                return
            await eval(comando)

    @commands.slash_command(name="msg", description="Comando para a Eery falar algo, apenas alguns podem utilizar :)")
    async def msg(self, inter : disnake.ApplicationCommandInteraction, mensagem : str, contem_variavel : bool = False):
        if inter.author.id in [self.client.owner.id, inter.guild.owner.id]:
            if contem_variavel:
                mensagem = eval(f"f'{mensagem}'")
                
            await inter.channel.send(mensagem)


    async def sleep_check_and_delete_role(self, role):
        await asyncio.sleep(10)
        return await self.check_and_delete_role(role)

    async def check_and_delete_role(self, role):
        if len(role.members) == 0:
            await role.delete()
            return True
        return False

    async def remove_colors(self, author):
        color_roles = []
        re_color = re.compile(r'^\#[0-9A-F]{6}$')
        for role in author.roles:
            if re_color.match(role.name.upper()):
                color_roles.append(role)

        for role in color_roles:
            await author.remove_roles(role)
            asyncio.create_task(self.sleep_check_and_delete_role(role))

        return len(color_roles)

    @commands.slash_command(name="cor", description="Muda a cor do seu nick no servidor")
    async def cor(self, inter : disnake.ApplicationCommandInteraction, cor : str):
        await inter.response.defer()

        author  = inter.author 
        guild   = inter.guild

        cor = cor.strip().upper()

        if cor == "REMOVER":
            removed = await self.remove_colors(author)
            if removed > 0:
                await inter.send("Cor removida!")
            else:
                await inter.send("Nenhuma cor para remover.")
            return
        
        if cor == "SEXO":
            await inter.send("Safada")
            return

        re_color = r'^\#[0-9A-F]{6}$'
        cor = "#" + cor if re.match(r'[0-9A-F]{6}$', cor) else cor

        if re.match(re_color, cor) is None:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

            cor = "#" + requests.get(
                f"https://www.colourlovers.com/api/colors?keywords={cor}&numResults=1&format=json", 
                headers=headers)\
            .json()[0]["hex"]

        await self.remove_colors(author)

        assigned_role = None

        for role in guild.roles:
            if role.name.upper() == cor:
                assigned_role = role

        if assigned_role == None:
            red   = int(cor[1:3], 16) 
            green = int(cor[3:5], 16) 
            blue  = int(cor[5:7], 16) 
            assigned_role = await guild.create_role(
                name=cor, 
                colour=disnake.Color.from_rgb(red, green, blue))

        await author.add_roles(assigned_role)

        await inter.edit_original_message(f"Cor adicionada!")

    @commands.slash_command(name="avatar", description="Retorna a imagem de perfil")
    async def avatar(self, inter : disnake.ApplicationCommandInteraction, usuario : disnake.User = None):
        await inter.response.defer()

        if usuario == None:
            usuario = inter.author

        embed = disnake.Embed(
            colour=disnake.Colour.blue(),
            title="Imagem de perfil de " + usuario.name
        )
        embed.set_image(url=usuario.display_avatar)

        await inter.edit_original_message(embed=embed)

    # por algum motivo n funciona no cog perfil
    @commands.slash_command(name="nome", description="Registra seu nome")
    async def nome(self, inter : disnake.ApplicationCommandInteraction, nome : str):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["nome"] = nome.strip().capitalize()
        salvar(membros)
        await inter.edit_original_message("Nome adicionado com sucesso!")


def setup(client: commands.Bot):
    client.add_cog(Comandos(client))
