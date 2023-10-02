import io
import disnake

from comandos.jogos.Uno.BaralhoUno import BaralhoUno
from comandos.jogos.Uno.JogadorUno import JogadorUno
from entidades.EeryType import EeryType


class Uno(disnake.ui.View):
    def __init__(self, mensagem_jogo : disnake.Message, bot : EeryType,
                 inter_jogador : disnake.ApplicationCommandInteraction, objeto_pai):
        super().__init__(timeout=300)
        self.mensagem = mensagem_jogo
        self.iniciado = False
        self.objeto_pai = objeto_pai
        self.bot = bot
        
        self.jogadores = []
        self.baralho = BaralhoUno()
        self.criador_jogo = JogadorUno(inter_jogador, self.baralho, self.bot, self)
        self.jogadores = [self.criador_jogo]
        self.atual = 0
        self.inverso = False
        
    async def on_timeout(self):
        self.objeto_pai.partida_uno = None
        
    def adicionar_jogador(self, inter : disnake.ApplicationCommandInteraction):
        self.jogadores.append(JogadorUno(inter, self.baralho, self.bot, self))
        
    def gerar_embed(self):
        embed = disnake.Embed(
            title="Partida de UNO sinistra",
            colour=disnake.Colour.blue()
        )
        if self.iniciado:
            embed.title += f" - Vez de {self.jogadores[self.atual].discord.display_name}"
            embed.set_image("attachment://image.png")
        
        else:
            embed.title += f" - Aguardando jogadores {len(self.jogadores)}/10..."
            embed.description = "Jogadores: " + ", ".join([f"<@{jogador.discord.id}>" for jogador in self.jogadores])
            
        return embed
        
    async def atualizar_jogo(self):
        if self.iniciado:
            with io.BytesIO() as image_binary:
                self.baralho.primeira_carta.imagem.save(image_binary, 'PNG')
                image_binary.seek(0)
                file = disnake.File(fp=image_binary, filename='image.png')
            await self.mensagem.edit(embed=self.gerar_embed(), view=self, file=file)
            return
        await self.mensagem.edit(embed=self.gerar_embed(), view=self)
          
    async def comecar_jogo(self):
        self.iniciado = True
        for jogador in self.jogadores:
            await jogador.inicio_partida(jogador == self.jogadores[self.atual])
        await self.atualizar_jogo()
    
    @disnake.ui.button(label="Iniciar partida", style=disnake.ButtonStyle.blurple)
    async def iniciar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        #if inter.user != self.criador_jogo.discord or len(self.jogadores) < 2:
        #    return
        
        self.remove_item(self.iniciar_partida)
        await self.comecar_jogo()
        
    @disnake.ui.button(label="Finalizar partida", style=disnake.ButtonStyle.blurple)
    async def finalizar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        if inter.user != self.criador_jogo.discord:
            return
        
        if " (Confirmação)" not in self.finalizar_partida.label:
            self.finalizar_partida.label += " (Confirmação)"
            await self.atualizar_jogo()
            return
        
        await self.mensagem.edit("Jogo finalizado", embed=None, view=None)
        self.objeto_pai.partida_uno = None
        del self
        