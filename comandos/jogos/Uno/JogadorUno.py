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
        self.selects : list[disnake.ui.Select] = []
        self.botoes = [self.botao_amarelo, self.botao_azul, self.botao_verde, self.botao_vermelho]
        
    async def inicio_partida(self, seu_turno : bool):
        self.mao.cartas = self.baralho.pegar_mao()
        self.mao.atualizar_options(self, self.baralho.carta_descarte)
        self.embed = disnake.Embed(
            title="Sua mão",
            colour=disnake.Colour.blurple()
        )
        self.embed.set_image("attachment://image.png")
        await self.inter.edit_original_message(
            content="Seu turno" if seu_turno else "Aguarde seu turno", embed=self.embed, view=self, file=self.mao.gerar_imagem())
        
    async def atualizar_status_jogar(self, comprar_ativo : bool) -> bool:
        return await self.atualizar_mensagem(seu_turno=True, comprar_ativo=comprar_ativo)
        
    async def atualizar_mensagem(self, seu_turno : bool, cor_selecao : bool = False, comprar_ativo : bool = False):
        content = "Aguarde seu turno"
        
        for select in self.selects:
            self.remove_item(select)
        self.selects = []
        
        if seu_turno:
            content = "Seu turno"
            if not cor_selecao:
                consegue_jogar = self.mao.atualizar_options(self, self.baralho.carta_descarte, comprar_ativo)
                if not consegue_jogar:
                    return False
            
        await self.inter.edit_original_message(
            content=content, embed=self.embed, view=self, file=self.mao.gerar_imagem())
        
        return True
        
    async def select_callback_jogar(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        
        carta_selecionada = [carta for carta in self.mao.cartas 
                             if inter.values[0] == f"{carta.cor}_{carta.simbolo}"][0]
        self.mao.cartas.remove(carta_selecionada)
        
        if not carta_selecionada.especial:
            await self.jogar(carta_selecionada)
        else:
            for botao in self.botoes:
                botao.carta = carta_selecionada
                botao.disabled = False
            await self.atualizar_mensagem(True, True)
    
    async def jogar(self, carta : Carta):
        self.baralho.jogar(carta)
        await self.atualizar_mensagem(False)
        await self.partida.jogar(carta)
                
    async def botao_selecionar_cor_callback(
            self, button : disnake.ui.Button, 
            inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        for botao in self.botoes:
            botao.disabled = True
        button.carta.cor = button.label.lower()
        await self.jogar(button.carta)
        
    @disnake.ui.button(label="Amarelo", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E8", disabled=True)
    async def botao_amarelo(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        await self.botao_selecionar_cor_callback(button, inter)
        
    @disnake.ui.button(label="Azul", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E6", disabled=True)
    async def botao_azul(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        await self.botao_selecionar_cor_callback(button, inter)
        
    @disnake.ui.button(label="Verde", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E9", disabled=True)
    async def botao_verde(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        await self.botao_selecionar_cor_callback(button, inter)
        
    @disnake.ui.button(label="Vermelho", style=disnake.ButtonStyle.blurple, emoji="\U0001F7E5", disabled=True)
    async def botao_vermelho(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
        await self.botao_selecionar_cor_callback(button, inter)
        
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

        def atualizar_options(self, jogador_view : disnake.ui.View, 
                              carta_descarte : Carta, comprar_ativo : bool = False) -> bool:
            self.cartas.sort(key=lambda carta: f"{carta.cor}_{carta.simbolo}")
            
            cartas : list[Carta] = []
            for self_carta in self.cartas:
                adicionar = True
                for carta in cartas:
                    if f"{self_carta.cor}_{self_carta.simbolo}" == f"{carta.cor}_{carta.simbolo}":
                        adicionar = False
                        break
                
                if adicionar and self.checar_valido(carta_descarte, self_carta, comprar_ativo):
                    cartas.append(self_carta)
            
            for a in range(math.ceil(len(cartas) / 25)):
                jogador_view.selects.append(
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
            
            if jogador_view.selects == []:
                return False
            
            for select in jogador_view.selects:
                select.callback = jogador_view.select_callback_jogar
                jogador_view.add_item(select)
            
            return True

        def checar_valido(self, carta_descarte : Carta, carta : Carta, comprar_ativo : bool) -> bool:
            if carta.simbolo == "+4":
                return True
            
            if not comprar_ativo:
                return carta_descarte.cor == carta.cor or carta_descarte.simbolo == carta.simbolo or carta.simbolo == "multicor"
            
            # +2 pra vc
            if comprar_ativo:
                #      +2 apenas em cima de +2
                return carta.simbolo == "+2" and carta_descarte.simbolo == "+2"
                