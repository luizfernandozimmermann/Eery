import json
import disnake
from disnake.ext import commands
import requests
from comandos.xp_funcoes import obter_xp
from entidades.Eery import Eery
from save_and_load import carregar, salvar


class Adm(commands.Cog):
    def __init__(self, bot : Eery):
        self.bot = bot
        self.usuario_servico = bot.usuario_servico
    
    @commands.slash_command(name="spam", description="Spam de mensagem. Representar variavel com {v}")
    async def spam(self, inter : disnake.ApplicationCommandInteraction, 
                   mensagem : str, quantidade : int, variavel : str = None):
        if inter.author.id not in [self.bot.owner.id, inter.guild.owner.id]:
            await inter.response.send_message("Você não tem permissão para usar esse comando.")
            return
        
        if variavel == None:
            for i in range(quantidade):
                await inter.channel.send(mensagem)
            return
        
        pos_var = 0
        variavel = variavel.split()
        for i in range(quantidade):
            v = variavel[pos_var]
            pos_var += 1
            if pos_var == len(variavel):
                pos_var = 0
            await inter.channel.send(eval(f"f'{mensagem}'"))
    
    @commands.slash_command(name="adm", description="Comando para manutenção do bot, apenas o desenvolvedor pode utilizar")
    async def adm(self, inter : disnake.ApplicationCommandInteraction, comando : str, assincrono : bool = True):
        if inter.author.id not in [self.bot.owner.id, inter.guild.owner.id]:
            await inter.response.send_message("Você não tem permissão para usar esse comando.")
            return
        if not assincrono:
            exec(comando)
            return
        await eval(comando)

    @commands.slash_command(name="msg", description="Comando para a Eery falar algo, apenas alguns podem utilizar :)")
    async def msg(self, inter : disnake.ApplicationCommandInteraction, mensagem : str, contem_variavel : bool = False):
        if inter.author.id not in [self.bot.owner.id, inter.guild.owner.id]:
            await inter.response.send_message("Você não tem permissão para usar esse comando.")
            return
        
        if contem_variavel:
            mensagem = eval(f"f'{mensagem}'")
            
        await inter.channel.send(mensagem)

    
    @commands.command(name="admhelp", description="Comando de help pros adm")
    async def admhelp(self, ctx : commands.Context):
        if ctx.author.id in [self.bot.owner.id, ctx.guild.owner.id]:
            embed = disnake.Embed(
                title="Lista de comando dos admin B)",
                colour=disnake.Colour.blue()
            )
            
            comandos = sorted(self.bot.commands, key=lambda x: x.name)

            for comando in comandos:
                parametros = ""
                
                for nome, param in comando.clean_params.items():
                    param = str(param.annotation)
                    param = param \
                        .removeprefix("typing.Union[").removesuffix("]").replace(", ", " | ") \
                        .removeprefix("<class '").removesuffix("'>")
                    
                    if param == "inspect._empty":
                        param = "any"
                    parametros += f"{nome}: {param}\n"
                
                parametros = None if parametros == "" else parametros
                    
                embed.add_field(
                    name=f"{comando.name}: {comando.description}",
                    value=parametros,
                    inline=False
                )
            await ctx.send(embed=embed)
    
    @commands.command(name="saving", description="Envia os dados atuais")
    async def saving(self, ctx : commands.Context, arquivo : str = "saving"):
        if ctx.author.id == self.bot.owner.id:
            with open(f"data/{arquivo}.json", "r") as f:
                file = disnake.File(f)
                await ctx.author.send(file=file)
                
    @commands.command(name="backup", description="Envie o backup para utilizar")
    async def backup(self, ctx : commands.Context, arquivo : str = "saving"):
        if ctx.author.id == self.bot.owner.id:
            content = json.loads(
                requests.get(ctx.message.attachments[0].url, allow_redirects=True).content.decode("utf-8")
                )
            salvar(content, arquivo=arquivo)

    @commands.command(name="config", description="Troca (ou mostra) config")
    async def config(self, ctx : commands.Context, *configs : str):
        if ctx.author.id == self.bot.owner.id:
            valor = configs[-1] if len(configs) > 1 else None
            configs = list(configs)[:-1] if len(configs) > 1 else None
            if configs == valor == None:
                embed = disnake.Embed(
                    title="Configs",
                    colour=disnake.Colour.blue()
                )
                for nome, valor in self.bot.configs.items():
                    tipo = str(type(valor)).removeprefix("<class '").removesuffix("'>")
                    embed.add_field(
                        name=nome,
                        value=f'{tipo}: {valor}',
                        inline=False
                    )
                await ctx.send(embed=embed)
                return
            
            comando = "self.bot.configs"
            for config in configs:
                comando += f"['{config}']"
            exec(f"{comando} = {valor}")
            salvar(self.bot.configs, "configs")
            await ctx.send("Bazinga!")

    
    @commands.command(name="resetxp", description="Reseta o xp de geral")
    async def resetxp(self, ctx: commands.Context):
        if ctx.author.id != self.bot.owner.id:
            return
        
        usuarios = self.usuario_servico.pegar_todos_usuarios()
        for usuario in usuarios:
            usuario.xp = 0
        self.usuario_servico.salvar_todos_usuarios(usuarios)    
        
        await ctx.send("AGORA DEU O CARAIO MEMO VIU, RESETOU FOI TUDO, RESETOU A PORRA TODA")
    
    @commands.command(name="setlvl", description="Seta o lvl da pessoa mencionada")
    async def setlvl(self, ctx : commands.Context, membro : disnake.Member | int, level : int):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        if type(membro) == int:
            membro = self.bot.get_user(membro)
        
        usuario = self.usuario_servico.pegar_usuario(membro)
        usuario.xp = obter_xp(level)
        self.usuario_servico.salvar_usuario(usuario)
        
        await ctx.send("Feito!")
    
    @commands.command(name="setxp", description="Seta o xp da pessoa mencionada")
    async def setxp(self, ctx : commands.Context, membro : disnake.Member | int, quantidade : int):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        if type(membro) == int:
            membro = self.bot.get_user(membro)
        
        usuario = self.usuario_servico.pegar_usuario(membro)
        usuario.xp = quantidade
        self.usuario_servico.salvar_usuario(usuario)
        
        await ctx.send("Feito!")
        
    @commands.command(name="addxp", description="Adiciona xp para pessoa mencionada")
    async def addxp(self, ctx : commands.Context, membro : disnake.Member | int, quantidade : int):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        if type(membro) == int:
            membro = self.bot.get_user(membro)
        
        usuario = self.usuario_servico.pegar_usuario(membro)
        usuario.xp += quantidade
        self.usuario_servico.salvar_usuario(usuario)
        
        await ctx.send("Feito!")
    
    @commands.command(name="setlvlexp", description="Seta o lvl e xp da pessoa mencionada")
    async def setlvlexp(self, ctx : commands.Context, membro : disnake.Member | int, level : int, xp : int):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        if type(membro) == int:
            membro = self.bot.get_user(membro)
        
        usuario = self.usuario_servico.pegar_usuario(membro)
        usuario.xp = obter_xp(level) + xp
        self.usuario_servico.salvar_usuario(usuario)
    
        await ctx.send("Feito!")
        
    @commands.command(name="addvalorcanal", description="Adiciona valor de xp para os ids de canais mencionados")
    async def addvalorxp(self, ctx : commands.Context, valor : float, *id_canais : str):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        valor_canais_xp = carregar("valor_canais_xp")
        valor = str(valor).replace(",", ".")
        
        canais = list(dict.fromkeys(id_canais))
        
        duplicatas = {
            
        }
        for valor, valor_canais in valor_canais_xp.items():
            for canal in canais:
                id_canal = int(canal.removeprefix("\u2060"))
                if id_canal in valor_canais:
                    duplicatas[valor] = id_canal
        
        for valor, id_canal in duplicatas.items():
            valor_canais_xp[valor].remove(id_canal)
        
        if valor in valor_canais_xp:
            for pos, canal in enumerate(canais):
                id_canal = int(canal.removeprefix("\u2060"))
                if id_canal not in valor_canais_xp[valor]:
                    try:
                        canais[pos] = self.bot.get_channel(id_canal).name
                        valor_canais_xp[valor].append(id_canal)
                    except:
                        await ctx.send(f"O id de canal {id_canal} não existe")
                        return
                else:
                    canais.remove(canal)
            
            if len(canais) != 0:
                salvar(valor_canais_xp, "valor_canais_xp")
                await ctx.send(f"Feito! Canal(is) {', '.join(canais)} adicionado(s) ao valor {valor}!")
            return
        
        canais_add = []
        nome_canais_add = []
        for pos, canal in enumerate(canais):
            try:
                id_canal = int(canal)
                nome_canal = self.bot.get_channel(id_canal).name
                nome_canais_add.append(nome_canal)
                canais_add.append(id_canal)
            except:
                pass
            
        valor_canais_xp[valor] = canais_add
        salvar(valor_canais_xp, "valor_canais_xp")
        await ctx.send(f"Feito! Criado o valor de {valor} para o(s) canal(is) {', '.join(nome_canais_add)}!")
        
    @commands.command(name="remvalorcanal", description="Remove o valor de xp para os ids de canais mencionados")
    async def remvalorxp(self, ctx : commands.Context, *id_canais : str):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        valor_canais_xp = carregar("valor_canais_xp")
        
        canais = list(dict.fromkeys(id_canais))
        
        removidos = []
        valor_apagar = []
        for canal in canais:
            for valor, canais_valor in valor_canais_xp.items():
                id_canal = int(canal.removeprefix("\u2060"))
                if id_canal in canais_valor:
                    valor_canais_xp[valor].remove(id_canal)
                    removidos.append(canal)
                    
                    if len(valor_canais_xp[valor]) == 0:
                        valor_apagar.append(valor)
                        
        for valor in valor_apagar:
            del valor_canais_xp[valor]
        
        for pos, canal in enumerate(removidos):
            if canal in canais:
                canais.remove(canal)
                id_canal = int(canal.removeprefix("\u2060"))
                removidos[pos] = self.bot.get_channel(id_canal).name
                
        for pos, canal in enumerate(canais):
            id_canal = int(canal.removeprefix("\u2060"))
            try:
                canais[pos] = self.bot.get_channel(id_canal).name
            except:
                await ctx.send(f"O id de canal {id_canal} não existe")
                return
        
        salvar(valor_canais_xp, "valor_canais_xp")
        await ctx.send(f"Feito! \nCanais removidos: {', '.join(removidos)}\nCanais não removidos: {', '.join(canais)}")
    
    @commands.command(name="limparvalorcanal", description="Limpa o valor de todos os canais com este valor")
    async def limparvalorxp(self, ctx : commands.Context, valor : float):
        if ctx.author.id not in [self.bot.owner.id, ctx.guild.owner.id]:
            return
        
        valor_canais_xp = carregar("valor_canais_xp")
        valor = str(valor).replace(",", ".")
        
        if valor not in valor_canais_xp:
            await ctx.send(f"O valor {valor} de canal não existe.")
            return

        del valor_canais_xp[valor]
        salvar(valor_canais_xp, "valor_canais_xp")
        await ctx.send(f"Valor {valor} de canal foi deletado!")
        

def setup(bot : Eery):
    bot.add_cog(Adm(bot))
