import random

from comandos.jogos.Uno.Carta import Carta


class BaralhoUno():
    def __init__(self):
        self.cartas : list[Carta] = []
        self.carta_descarte = None
        self.embaralhar()
        for carta in self.cartas:
            if carta.simbolo.isnumeric() and "+" not in carta.simbolo:
                self.jogar(carta)
                self.cartas.remove(carta)
                break
        
    def pegar_mao(self) -> list[Carta]:
        return [self.pegar_carta() for a in range(0, 7)]
        
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
            
            for especial in especiais:
                for a in range(0, 4):
                    self.cartas.append(Carta(simbolo=especial))
            
            for cor in cores:
                for simbolo in simbolos:
                    self.cartas.append(Carta(cor=cor, simbolo=simbolo))
                    self.cartas.append(Carta(cor=cor, simbolo=simbolo))
                 
            if self.carta_descarte != None:
                self.cartas.remove(self.carta_descarte)
                        
        random.shuffle(self.cartas)
    
    def jogar(self, carta : Carta):
        self.carta_descarte = carta
    