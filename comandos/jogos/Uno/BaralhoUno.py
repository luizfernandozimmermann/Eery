import random

from disnake import Emoji

from comandos.jogos.Uno.Carta import Carta
from entidades.EeryType import EeryType


class BaralhoUno():
    def __init__(self, bot : EeryType):
        self.bot = bot
        self.cartas : list[Carta] = []
        self.carta_descarte = None
        self.embaralhar()
        for carta in self.cartas:
            if carta.simbolo.isnumeric() and "+" not in carta.simbolo:
                self.jogar(carta)
                self.cartas.remove(carta)
                break
        
    def pegar_carta(self) -> Carta:
        carta = self.cartas[random.randint(0, len(self.cartas) - 1)]
        self.cartas.remove(carta)
        if self.cartas == []:
            self.embaralhar()
        return carta

    def embaralhar(self):
        if self.cartas == []:
            cores = ["amarelo", "azul", "verde", "vermelho"]
            simbolos = [str(a) for a in range(0, 10)]
            simbolos.append("bloqueio")
            simbolos.append("reverse")
            simbolos.append("+2")
            especiais = [ "+4", "multicor"]
            
            emojis : list[Emoji] = []
            for guild in self.bot.guilds:
                for emoji in guild.emojis:
                    emojis.append(emoji)
            
            for especial in especiais:
                for a in range(0, 4):
                    self.cartas.append(
                        Carta(simbolo=especial, 
                            emoji=[emoji for emoji in emojis if 
                                emoji.name.__contains__(f"especial_{especial.replace('+', 'mais')}")][0])
                        )
            
            for cor in cores:
                for simbolo in simbolos:
                    emoji = [emoji for emoji in emojis if 
                                emoji.name.__contains__(f"{cor}_{simbolo.replace('+', 'mais')}")][0]
                    
                    self.cartas.append(Carta(cor=cor, simbolo=simbolo, emoji=emoji))
                    self.cartas.append(Carta(cor=cor, simbolo=simbolo, emoji=emoji))
                 
            if self.carta_descarte != None:
                self.cartas.remove(self.carta_descarte)
                        
        random.shuffle(self.cartas)
    
    def jogar(self, carta : Carta):
        self.carta_descarte = carta
    