import disnake
from disnake.ext import commands
from comandos.jogos.JogoVelha.JogoVelha import JogoVelha
from comandos.jogos.Uno.Uno import Uno

from entidades.EeryType import EeryType


class Jogos(commands.Cog):
    def __init__(self, bot : EeryType):
        self.bot = bot
        self.partida_uno = None

    @commands.slash_command(name="jogo_velha", description="Jogo da velha :)")
    async def jogo_velha(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        view = JogoVelha(inter.author)
        embed = view.gerar_embed(inter.author.name)
        await inter.edit_original_message(embed=embed, view=view, file=view.jogo_mapa.gerar_mapa())

    @commands.slash_command(name="uno", description="Inicia uma partida de UNO")
    async def uno_iniciar(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        
        if self.partida_uno == None:
            mensagem_jogo = await inter.channel.send(embed=disnake.Embed(title="Iniciando partida..."))
            self.partida_uno = Uno(mensagem_jogo, self.bot, inter, self)
            await self.partida_uno.atualizar_jogo()
            await inter.edit_original_message("Jogo criado! Clique em Iniciar partida quando estiver pronto! (Não apague essa mensagem)")
            
        elif not self.partida_uno.iniciado:
            if len(self.partida_uno.jogadores) == 5:
                await inter.edit_original_message("Máximo de jogadores atingido.")
                return
            
            if inter.user.id in [jogador.discord.id for jogador in self.partida_uno.jogadores]:
                await inter.edit_original_message("Esta será sua nova mensagem da partida. (Não apague essa mensagem)")
                jogador = next((jogador for jogador in self.partida_uno.jogadores if jogador.discord == inter.user))
                jogador.inter = inter
                return
                
            self.partida_uno.adicionar_jogador(inter)
            await inter.edit_original_message("Entrou na partida! Espere o criador do jogo iniciar a partida. (Não apague essa mensagem)")
        
        else:
            await inter.edit_original_message("Há uma partida de Uno ocorrendo no momento, favor espere acabar.")
