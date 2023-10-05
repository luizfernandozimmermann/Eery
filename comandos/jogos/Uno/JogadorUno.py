import io
import math
from typing import Optional
import disnake
from PIL import Image
from disnake.interactions import MessageInteraction
from disnake.ui.item import Item

from comandos.jogos.Uno.BaralhoUno import BaralhoUno
from comandos.jogos.Uno.Carta import Carta
from entidades.EeryType import EeryType


class JogadorUno():
    def __init__(self, inter : disnake.ApplicationCommandInteraction, baralho : BaralhoUno, bot : EeryType, partida):
        self.view = self.JogadorUnoView(inter, self, bot)
        
        self.baralho = baralho
        self.discord = inter.user
        self.bot = bot
        self.mao : list[Carta] = []
        self.uno = False
        
        self.partida = partida
        
    async def inicio_partida(self, seu_turno : bool):
        self.mao = self.comprar(7)
        await self.view.inicio_partida(seu_turno)
        
    async def atualizar_status_jogar(self, comprar_ativo : bool):
        await self.view.atualizar_mensagem(seu_turno=True, comprar_ativo=comprar_ativo)
        
    async def jogar(self, carta : Carta):
        await self.view.atualizar_mensagem(False)
        await self.partida.jogar(carta)

    def comprar(self, quantidade : int) -> Carta | list[Carta]:
        self.uno = False
        cartas_pegas = []
        for i in range(quantidade):
            carta_pega = self.baralho.pegar_carta()
            cartas_pegas.append(carta_pega)
            self.mao.append(carta_pega)
        self.mao.sort(key=lambda carta: (not carta.especial, carta.cor, carta.simbolo))
        
        return cartas_pegas[0] if len(cartas_pegas) == 1 else cartas_pegas


    class JogadorUnoView(disnake.ui.View):
        def __init__(self, inter : disnake.ApplicationCommandInteraction, jogador, bot : EeryType) -> None:
            super().__init__(timeout=300)
            self.jogador : JogadorUno = jogador
            self.bot = bot
            self.inter = inter
            self.seu_turno = False
            
            # Cartas por linha
            self.cpl = 10
            
            self.selects : list[disnake.ui.Select] = []
            self.botoes = [self.botao_amarelo, self.botao_azul, self.botao_verde, self.botao_vermelho]
            for botao in self.botoes:
                self.remove_item(botao)
        
        async def on_error(self, error: Exception, item: Item, interaction: MessageInteraction) -> None:
            await self.atualizar_mensagem(self.seu_turno)
        
        async def trocar_mensagem(self, inter : disnake.ApplicationCommandInteraction):
            self.id
            self.inter = inter
            await self.mensagem.delete()
            self.mensagem = await inter.edit_original_message(
                embed=self.embed,
                file=self.gerar_imagem(),
                view=self
            )

        async def inicio_partida(self, seu_turno : bool):
            self.remove_item(self.uno)
            if not seu_turno:
                self.remove_item(self.botao_comprar)
            else:
                self.atualizar_options(self.jogador.baralho.carta_descarte)
            
            self.embed = disnake.Embed(
                title="Sua mão",
                colour=disnake.Colour.blurple()
            )
            self.embed.set_image("attachment://image.png")
            
            self.mensagem = await self.inter.edit_original_message(
                content="Seu turno" if seu_turno else "Aguarde seu turno", embed=self.embed, view=self, file=self.gerar_imagem())
        
        def checar_consegue_jogar(self, carta_descarte : Carta, comprar_ativo : bool):
            return self.pegar_cartas_validas(carta_descarte, comprar_ativo) != []
        
        async def atualizar_mensagem(self, seu_turno : bool, cor_selecao : bool = False, comprar_ativo : bool = False):
            content = "Aguarde seu turno"
            self.seu_turno = seu_turno
            
            for select in self.selects:
                self.remove_item(select)
            self.selects = []
            self.remove_item(self.botao_comprar)
            self.remove_item(self.uno)
            
            if seu_turno:
                content = "Seu turno"
                if len(self.jogador.mao) == 2 and self.checar_consegue_jogar(self.jogador.baralho.carta_descarte, comprar_ativo):
                    if not self.jogador.uno:
                        self.uno.disabled = False
                    self.add_item(self.uno)
                else:
                    self.remove_item(self.uno)
                if not cor_selecao:
                    self.add_item(self.botao_comprar)
                    carta_descarte = self.jogador.baralho.carta_descarte
                    self.atualizar_options(carta_descarte, comprar_ativo)
            
            imagem = self.gerar_imagem()
            if imagem != None:
                self.mensagem = await self.inter.edit_original_message(
                    content=content, embed=self.embed, view=self, file=imagem)
            else:
                await self.inter.edit_original_message(
                    content="Parabéns! Suas cartas acabaram!", embed=None, view=self, attachments=None)
                        
        async def select_callback_jogar(self, inter: disnake.MessageInteraction):
            await inter.response.defer()
            
            carta_selecionada = [carta for carta in self.jogador.mao 
                                if inter.values[0] == f"{carta.cor}_{carta.simbolo}"][0]
            self.jogador.mao.remove(carta_selecionada)
            
            if not carta_selecionada.especial:
                await self.jogador.jogar(carta_selecionada)
            else:
                for botao in self.botoes:
                    botao.carta = carta_selecionada
                    self.add_item(botao)
                await self.atualizar_mensagem(True, True)
        
        def gerar_imagem(self) -> disnake.File | None:
            if len(self.jogador.mao) == 0:
                return None
            pos_x = 0
            pos_y = 0
            imagem_mao = Image.new("RGBA", 
                (64 * self.cpl if len(self.jogador.mao) >= self.cpl else len(self.jogador.mao) * 64, 
                 math.ceil(len(self.jogador.mao) / self.cpl) * 96)
            )
            
            for carta in self.jogador.mao:
                imagem_mao.paste(carta.imagem, (pos_x * 64, pos_y * 96), carta.imagem)
                pos_x += 1
                if pos_x == self.cpl:
                    pos_x = 0
                    pos_y += 1
            
            with io.BytesIO() as image_binary:
                imagem_mao.save(image_binary, 'PNG')
                image_binary.seek(0)
                return disnake.File(fp=image_binary, filename='image.png')

        def atualizar_options(self, carta_descarte : Carta, comprar_ativo : bool = False):
            self.jogador.mao.sort(key=lambda carta: f"{carta.cor}_{carta.simbolo}")
            def remover_selects():
                for select in self.selects:
                    select.callback = self.select_callback_jogar
                    self.remove_item(select)
                    
            def adicionar_selects(cartas : list[Carta]):
                for a in range(math.ceil(len(cartas) / 25)):
                    self.selects.append(
                        disnake.ui.Select(
                            placeholder="Escolha sua carta!",
                            options= [disnake.SelectOption(
                                label=f"{carta.cor.capitalize()} {carta.simbolo.capitalize()}",
                                value= f"{carta.cor}_{carta.simbolo}",
                                emoji=carta.emoji
                            ) for carta in cartas if a * 25 <= cartas.index(carta) < (a + 1) * 25]
                                )
                    )
                    
                for select in self.selects:
                    select.callback = self.select_callback_jogar
                    self.add_item(select)
            
            remover_selects()
            adicionar_selects(self.pegar_cartas_validas(carta_descarte, comprar_ativo))

        def pegar_cartas_validas(self, carta_descarte : Carta, comprar_ativo : bool) -> list[Carta]:
            cartas : list[Carta] = []
            for self_carta in self.jogador.mao:
                adicionar = True
                for carta in cartas:
                    if f"{self_carta.cor}_{self_carta.simbolo}" == f"{carta.cor}_{carta.simbolo}":
                        adicionar = False
                        break
                
                if adicionar and self.checar_carta_valida(carta_descarte, self_carta, comprar_ativo):
                    cartas.append(self_carta)
            return cartas
        
        def checar_carta_valida(self, carta_descarte : Carta, carta : Carta, comprar_ativo : bool) -> bool:
            if carta.simbolo == "+4":
                return True
            
            if not comprar_ativo:
                return carta_descarte.cor == carta.cor or carta_descarte.simbolo == carta.simbolo or carta.simbolo == "multicor"
            
            # +2 pra vc
            if comprar_ativo:
                #      +2 apenas em cima de +2
                return carta.simbolo == "+2" and carta_descarte.simbolo == "+2"
   
        async def botao_selecionar_cor_callback(
                self, button : disnake.ui.Button, 
                inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            
            for botao in self.botoes:
                self.remove_item(botao)
                
            button.carta.cor = button.label.lower()
            await self.jogador.jogar(button.carta)
            
        @disnake.ui.button(label="Amarelo", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E8")
        async def botao_amarelo(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao_selecionar_cor_callback(button, inter)
            
        @disnake.ui.button(label="Azul", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E6")
        async def botao_azul(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao_selecionar_cor_callback(button, inter)
            
        @disnake.ui.button(label="Verde", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E9")
        async def botao_verde(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao_selecionar_cor_callback(button, inter)
            
        @disnake.ui.button(label="Vermelho", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E5")
        async def botao_vermelho(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao_selecionar_cor_callback(button, inter)
         
        @disnake.ui.button(label="Comprar", style=disnake.ButtonStyle.blurple)
        async def botao_comprar(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            if self.jogador.partida.quantidade_comprar != 0:
                self.jogador.comprar(self.jogador.partida.quantidade_comprar)
                self.jogador.partida.quantidade_comprar = 0
                self.jogador.partida.pular_jogador()
                await self.jogador.partida.atualizar_jogador_atual()
                await self.atualizar_mensagem(False)
                
            else:
                carta_descarte = self.jogador.baralho.carta_descarte
                carta_pega = self.jogador.comprar(1)
                while not self.checar_carta_valida(carta_descarte, carta_pega, False):
                    carta_pega = self.jogador.comprar(1)

                await self.atualizar_mensagem(True)
                
        @disnake.ui.button(label="UNO", style=disnake.ButtonStyle.red)
        async def uno(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await inter.response.defer()
            if len(self.selects) > 0:
                self.jogador.uno = True
                self.uno.disabled = True
                await self.atualizar_mensagem(True)
                