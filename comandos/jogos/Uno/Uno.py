import io
from typing import Optional
import disnake

from comandos.jogos.Uno.BaralhoUno import BaralhoUno
from comandos.jogos.Uno.Carta import Carta
from comandos.jogos.Uno.JogadorUno import JogadorUno
from entidades.EeryType import EeryType


class Uno():
    def __init__(self, mensagem_jogo : disnake.Message, bot : EeryType,
                 inter_jogador : disnake.ApplicationCommandInteraction, objeto_pai):
        self.iniciado = False
        self.objeto_pai = objeto_pai
        self.bot = bot
        
        self.baralho = BaralhoUno()
        self.criador_jogo = JogadorUno(inter_jogador, self.baralho, self.bot, self)
        self.jogadores = [self.criador_jogo]
        self.atual = 0
        self.quantidade_comprar = 0
        self.inverso = False
        
        self.view = self.UnoView(mensagem_jogo, bot, self)
        
    async def adicionar_jogador(self, inter : disnake.ApplicationCommandInteraction):
        self.jogadores.append(JogadorUno(inter, self.baralho, self.bot, self))
        await self.view.atualizar_jogo()
     
    async def jogar(self, carta : Carta):
        self.baralho.jogar(carta)
        
        # aplica regras de carta
        # TODO: arrumar carta bloqueio, ele ta fazendo o jogador escolher a cor (?) (teste feito com 2 pessoas apenas)
        quantidade_pular = 1
        if carta.simbolo == "bloqueio":
            quantidade_pular += 1
        
        if "+" in carta.simbolo:
            self.quantidade_comprar += int(carta.simbolo)
        
        elif carta.simbolo == "reverse":
            self.inverso = not self.inverso
            
        self.pular_jogador(quantidade_pular)
        await self.atualizar_jogador_atual()
          
    async def atualizar_jogador_atual(self):
        jogador_atual = self.jogadores[self.atual]
        await jogador_atual.atualizar_status_jogar(self.quantidade_comprar != 0)
        await self.view.atualizar_jogo()
                
    def pular_jogador(self, quantidade : int = 1):
        if self.inverso:
            for i in range(quantidade):
                self.atual -= 1
                if self.atual < 0:
                    self.atual = len(self.jogadores) - 1
        else:
            for i in range(quantidade):
                self.atual += 1
                if self.atual >= len(self.jogadores):
                    self.atual = 0
        
    async def comecar_jogo(self):
        self.iniciado = True
        for jogador in self.jogadores:
            await jogador.inicio_partida(jogador == self.jogadores[self.atual])
        await self.view.atualizar_jogo()
    
    class UnoView(disnake.ui.View):
        def __init__(self, mensagem : disnake.Message, bot : EeryType, partida) -> None:
            super().__init__(timeout=300)
            self.mensagem = mensagem
            self.bot = bot
            self.partida : Uno = partida
            
        async def on_timeout(self):
            self.partida.objeto_pai.partida_uno = None
            
        def gerar_embed(self):
            embed = disnake.Embed(
                title="Partida de UNO sinistra",
                colour=disnake.Colour.blue()
            )
            if self.partida.iniciado:
                embed.title += f"Esperando jogada de {self.partida.jogadores[self.partida.atual].discord.display_name}"
                
                sinal = " -> " if not self.partida.inverso else " <- "
                embed.description = "Ordem de jogadores: " + \
                    f"..{sinal}{sinal.join([f'<@{jogador.discord.id}>' for jogador in self.partida.jogadores])}{sinal}"
                embed.title += f" - Vez de {self.partida.jogadores[self.partida.atual].discord.display_name}"
                
                if self.partida.baralho.carta_descarte.especial:
                    embed.description += f"\nCor selecionada: {self.partida.baralho.carta_descarte.cor.capitalize()}"
                if self.partida.quantidade_comprar != 0:
                    embed.description += f"\nO próximo irá comprar {self.partida.quantidade_comprar} cartas!"
                    
                embed.set_image("attachment://image.png")
            
            else:
                embed.title += f" - Aguardando jogadores {len(self.partida.jogadores)}/10..."
                embed.description = "Jogadores: " + ", ".join([f"<@{jogador.discord.id}>" for jogador in self.partida.jogadores])
                
            return embed
            
        async def atualizar_jogo(self):
            if self.partida.iniciado:
                with io.BytesIO() as image_binary:
                    self.partida.baralho.carta_descarte.imagem.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    file = disnake.File(fp=image_binary, filename='image.png')
                await self.mensagem.edit(embed=self.gerar_embed(), view=self, file=file)
                return
            await self.mensagem.edit(embed=self.gerar_embed(), view=self)
            
        @disnake.ui.button(label="Iniciar partida", style=disnake.ButtonStyle.blurple)
        async def iniciar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            # TODO: quando estiver pronto pra jogar
            #if inter.user != self.criador_jogo.discord or len(self.jogadores) < 2:
            #    return
            
            self.remove_item(self.iniciar_partida)
            await self.partida.comecar_jogo()
            await inter.response.defer()
            
        @disnake.ui.button(label="Finalizar partida", style=disnake.ButtonStyle.blurple)
        async def finalizar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            if inter.user != self.partida.criador_jogo.discord:
                return
            
            if " (Confirmação)" not in self.finalizar_partida.label:
                self.finalizar_partida.label += " (Confirmação)"
                await self.atualizar_jogo()
                return
            
            await self.mensagem.edit("Jogo finalizado", embed=None, view=None)
            self.partida.objeto_pai.partida_uno = None
            del self.partida
            del self
        