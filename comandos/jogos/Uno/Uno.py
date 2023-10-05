from datetime import datetime
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
        
        self.baralho = BaralhoUno(bot)
        self.criador_jogo = JogadorUno(inter_jogador, self.baralho, self.bot, self)
        self.jogadores = [self.criador_jogo]
        self.ordem_ganhadores : list[JogadorUno] = []
        self.atual = 0
        self.quantidade_comprar = 0
        self.inverso = False
        
        self.horario_inicio = datetime.now()
        self.view = self.UnoView(mensagem_jogo, bot, self)
        
    async def adicionar_jogador(self, inter : disnake.ApplicationCommandInteraction):
        self.jogadores.append(JogadorUno(inter, self.baralho, self.bot, self))
        await self.view.atualizar_jogo()
     
    async def jogar(self, carta : Carta):
        jogador = self.jogadores[self.atual]
        remover_jogador = False
        if len(jogador.mao) == 0:
            remover_jogador = True
            self.ordem_ganhadores.append(jogador)
        
        elif len(jogador.mao) == 1 and not jogador.uno:
            self.view.uno.disabled = False
            
        self.baralho.jogar(carta)
        
        # aplica regras de carta
        quantidade_pular = 1
        if carta.simbolo == "bloqueio":
            quantidade_pular += 1
        
        if "+" in carta.simbolo:
            self.quantidade_comprar += int(carta.simbolo)
        
        elif carta.simbolo == "reverse":
            self.inverso = not self.inverso
                
        self.pular_jogador(quantidade_pular)
        
        await self.atualizar_jogador_atual()
        
        if remover_jogador:
            self.jogadores.remove(jogador)
            
            if len(self.jogadores) == 1:
                await self.finalizar_jogo()
                return
        
        await self.view.atualizar_jogo()
        
    async def atualizar_jogador_atual(self):
        jogador_atual = self.jogadores[self.atual]
        await jogador_atual.atualizar_status_jogar(self.quantidade_comprar != 0)
                
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
        self.view.add_item(self.view.uno)
        for jogador in self.jogadores:
            await jogador.inicio_partida(jogador == self.jogadores[self.atual])
        await self.view.atualizar_jogo()
    
    async def finalizar_jogo(self):
        for jogador in self.jogadores:
            await jogador.view.inter.edit_original_message(view=None)
        
        for jogador in self.ordem_ganhadores:
            await jogador.view.inter.edit_original_message(view=None)
        
        embed_final = disnake.Embed(
            title="Partida de UNO Sinistro - Finalizado",
            colour=disnake.Colour.blue()
        )
        if len(self.ordem_ganhadores) > 0:
            embed_final.add_field(
                name="Ordem dos ganhadores",
                value=", ".join([jogador.discord.display_name for jogador in self.ordem_ganhadores]),
                inline=False
            )
        
        duracao = datetime.now() - self.horario_inicio
        embed_final.add_field(
            name="Duração da partida",
            value=f"{duracao.seconds // 60} minutos e {duracao.seconds % 60} segundos",
            inline=False
        )
        
        if self.ordem_ganhadores == []:
            embed_final.description = "Sem vencedores."
        await self.view.mensagem.edit(embed=embed_final, view=None, attachments=None)
        self.objeto_pai.partida_uno = None
        del self
    
    
    class UnoView(disnake.ui.View):
        def __init__(self, mensagem : disnake.Message, bot : EeryType, partida) -> None:
            super().__init__(timeout=300)
            self.mensagem = mensagem
            self.bot = bot
            self.partida : Uno = partida
            self.remove_item(self.uno)
            
        async def on_timeout(self):
            self.partida.objeto_pai.partida_uno = None
            
        def gerar_embed(self):
            embed = disnake.Embed(
                title="Partida de UNO sinistra",
                colour=disnake.Colour.blue()
            )
            if self.partida.iniciado:                
                embed.title += f" - Vez de {self.partida.jogadores[self.partida.atual].discord.display_name}"
                
                if len(self.partida.ordem_ganhadores) > 0:
                    embed.add_field(
                        name="Ordem dos ganhadores",
                        value=", ".join([jogador.discord.display_name for jogador in self.partida.ordem_ganhadores])
                    )
                    
                jogadores = sorted(self.partida.jogadores, key=lambda jogador: len(jogador.mao))
                texto = ""
                for jogador in jogadores:
                    texto += f"\n{jogador.discord.display_name}: {len(jogador.mao)} cartas"
                embed.add_field(
                    name="Quantidade de cartas dos jogadores",
                    value=texto[1:]
                )
                
                sinal = " -> " if not self.partida.inverso else " <- "
                embed.add_field(
                    name="Ordem dos jogadores",
                    value=f"..{sinal}{sinal.join([f'<@{jogador.discord.id}>' for jogador in self.partida.jogadores])}{sinal}"
                )
                
                if self.partida.baralho.carta_descarte.especial:
                    emojis = {
                        "Amarelo": "\U0001F7E8",
                        "Azul": "\U0001F7E6",
                        "Verde": "\U0001F7E9",
                        "Vermelho": "\U0001F7E5"
                    }
                    cor = self.partida.baralho.carta_descarte.cor.capitalize()
                    emoji = emojis[cor]
                    embed.add_field(
                        name="Cor selecionada",
                        value=f"{emoji} {cor} {emoji}",
                        inline=False
                    )
                    
                if self.partida.quantidade_comprar != 0:
                    embed.add_field(
                        name="Acúmulo de maldade",
                        value=f"O próximo jogador irá comprar {self.partida.quantidade_comprar} cartas!"
                    )
                
                embed.set_footer(text="Botão 'UNO!' desta mensagem ficará disponível quando algum jogador não falar UNO! antes de jogar a sua penúltima carta. /uno irá reenviar sua mensagem com as suas cartas.")
                
                embed.set_image("attachment://image.png")
            
            else:
                embed.title += f" - Aguardando jogadores {len(self.partida.jogadores)}/10..."
                embed.description = "Jogadores: " + ", ".join([f"<@{jogador.discord.id}>" for jogador in self.partida.jogadores])
                embed.set_footer(text="/uno para entar na partida. Apenas o criador da partida consegue iniciá-la.")
                
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
            
        @disnake.ui.button(label="UNO!", style=disnake.ButtonStyle.red, disabled=True)
        async def uno(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            jogadores_nao_uno = [jogador for jogador in self.partida.jogadores if not jogador.uno and len(jogador.mao) == 1]
            if inter.user.id in [jogador.discord.id for jogador in jogadores_nao_uno]:
                return
            
            for jogador in jogadores_nao_uno:
                jogador.comprar(2)
                await jogador.view.atualizar_mensagem(False)
            embed = self.gerar_embed()
            embed.add_field(
                name="UNO! não dito!",
                value=f"Jogador {inter.user.display_name} fez {', '.join(x.discord.display_name for x in jogadores_nao_uno)} comprar(em) 2 cartas por não falar UNO!"
            )
            await self.mensagem.edit(embed=embed, view=self)
            self.uno.disabled = True
            
        @disnake.ui.button(label="Iniciar partida", style=disnake.ButtonStyle.blurple)
        async def iniciar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            if inter.user != self.partida.criador_jogo.discord or len(self.partida.jogadores) < 2:
                return
            
            self.remove_item(self.iniciar_partida)
            await self.partida.comecar_jogo()
            
        @disnake.ui.button(label="Finalizar partida", style=disnake.ButtonStyle.blurple)
        async def finalizar_partida(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            if inter.user != self.partida.criador_jogo.discord:
                return
            
            if " (Confirmação)" not in self.finalizar_partida.label:
                self.finalizar_partida.label += " (Confirmação)"
                await self.atualizar_jogo()
                return
            
            await self.partida.finalizar_jogo()
        