import io
import math
import disnake
from PIL import Image

from comandos.jogos.Uno.BaralhoUno import BaralhoUno
from comandos.jogos.Uno.Carta import Carta
from entidades.EeryType import EeryType


class JogadorUno(disnake.ui.View):
    def __init__(self, inter : disnake.ApplicationCommandInteraction, baralho : BaralhoUno, bot : EeryType, partida):
        super().__init__(timeout=300)
        self.inter = inter
        self.baralho = baralho
        self.discord = inter.user
        self.bot = bot
        self.mao = self.Mao(bot)
        self.partida = partida
        
    async def inicio_partida(self, seu_turno : bool):
        self.mao.cartas = self.baralho.pegar_mao()
        self.mao.atualizar_options(self)
        embed = disnake.Embed(
            title="Sua mão",
            colour=disnake.Colour.blurple()
        )
        embed.set_image("attachment://image.png")
        await self.inter.edit_original_message(
            content="Seu turno" if seu_turno else "Aguarde seu turno", embed=embed, view=self, file=self.mao.gerar_imagem())
        
    async def atualizar_mensagem(self, seu_turno : bool):
        embed = disnake.Embed(
            title="Sua mão",
            colour=disnake.Colour.blurple()
        )
        embed.set_image("attachment://image.png")
        
        if seu_turno:
            self.mao.atualizar_options(self)
            await self.inter.edit_original_message(content="Seu turno", embed=embed, view=self, file=self.mao.gerar_imagem())
            return
        
        await self.inter.edit_original_message(content="Aguarde seu turno", embed=embed, view=None, file=self.mao.gerar_imagem())
        
    async def select_callback_jogar(self, inter: disnake.MessageInteraction):
        carta_selecionada = [carta for carta in self.mao.cartas 
                             if inter.values[0] == f"{carta.cor}_{carta.simbolo}"][0]
        self.baralho.jogar(carta_selecionada)
        self.mao.cartas.remove(carta_selecionada)
        await self.atualizar_mensagem(False)
        await self.partida.atualizar_jogo()
        
    class Mao():
        def __init__(self, bot : EeryType):
            self.cartas : list[Carta] = []
            # cartas por linha
            self.cpl = 10
            self.bot = bot
            
        def gerar_imagem(self) -> disnake.File:
            pos_x = 0
            pos_y = 0
            imagem_mao = Image.new("RGBA", 
                (64 * self.cpl if len(self.cartas) >= self.cpl else len(self.cartas) * 64, 
                 math.ceil(len(self.cartas) / self.cpl) * 96)
            )
            
            for carta in self.cartas:
                imagem_mao.paste(carta.imagem, (pos_x * 64, pos_y * 96), carta.imagem)
                pos_x += 1
                if pos_x == self.cpl:
                    pos_x = 0
                    pos_y += 1
            
            with io.BytesIO() as image_binary:
                imagem_mao.save(image_binary, 'PNG')
                image_binary.seek(0)
                return disnake.File(fp=image_binary, filename='image.png')

        def atualizar_options(self, jogador_view : disnake.ui.View, ultima_carta_descarte : Carta):
            for item in jogador_view.children:
                jogador_view.remove_item(item)
            
            self.cartas.sort(key=lambda carta: f"{carta.cor}_{carta.simbolo}")
            
            cartas : list[Carta] = []
            for self_carta in self.cartas:
                adicionar = True
                for carta in cartas:
                    if f"{self_carta.cor}_{self_carta.simbolo}" == f"{carta.cor}_{carta.simbolo}":
                        adicionar = False
                        break
                
                if adicionar and (
                    self_carta.cor == ultima_carta_descarte.cor or 
                    self_carta.simbolo == ultima_carta_descarte.simbolo or
                    self_carta.especial
                ):
                    cartas.append(self_carta)
            
            for a in range(math.ceil(len(cartas) / 25)):
                jogador_view.add_item(
                    disnake.ui.Select(
                        placeholder="Escolha sua carta!",
                        options= [disnake.SelectOption(
                            label=f"{carta.cor.capitalize()} {carta.simbolo.capitalize()}",
                            value= f"{carta.cor}_{carta.simbolo}",
                            emoji=next(
                                disnake.utils.get(i.emojis, name=f"{carta.cor}_{carta.simbolo.replace('+', 'mais')}") 
                                for i in self.bot.guilds)
                        ) for carta in cartas if a * 25 <= cartas.index(carta) < (a + 1) * 25]
                            )
                )
            
            for item in jogador_view.children:
                item.callback = jogador_view.select_callback_jogar
