import io
from random import randint
from PIL import Image
import disnake


class JogoVelhaMapa():
    def __init__(self):
        self.contagem = 0
        self.tabela_jogo = [[" ", " ", " "],
                    [" ", " ", " "],
                    [" ", " ", " "]]
        
        self.imagem_mapa = Image.open("comandos/jogos/JogoVelha/imagens/fundo.png")
        self.finalizado = False

    def jogar(self, linha : int, coluna : int, letra : str):
        self.contagem += 1
        self.tabela_jogo[linha][coluna] = letra
        imagem_letra = Image.open(f"comandos/jogos/JogoVelha/imagens/player_{letra.lower()}.png")
        self.imagem_mapa.paste(imagem_letra, (coluna * 210, linha * 210))
        self.finalizado = self.checar_vitoria("X") or self.checar_vitoria("O")
    
    def gerar_mapa(self):
        with io.BytesIO() as imagem:
            self.imagem_mapa.save(imagem, 'PNG')
            imagem.seek(0)
            return disnake.File(fp=imagem, filename='image.png')
    
    def jogada_bot(self):
        preferencia = []
        possibilidades = []

        # horizontal
        for c in range(0, 3):
            if self.tabela_jogo[c][0] == self.tabela_jogo[c][1] and \
                    self.tabela_jogo[c][0] != " " and self.tabela_jogo[c][2] == " ":
                if self.tabela_jogo[c][0] == "X":
                    preferencia.append([c, 2])
                possibilidades.append([c, 2])

            if self.tabela_jogo[c][0] == self.tabela_jogo[c][2] and \
                    self.tabela_jogo[c][0] != " " and self.tabela_jogo[c][1] == " ":
                if self.tabela_jogo[c][0] == "X":
                    preferencia.append([c, 1])
                possibilidades.append([c, 1])

            if self.tabela_jogo[c][1] == self.tabela_jogo[c][2] and \
                    self.tabela_jogo[c][1] != " " and self.tabela_jogo[c][0] == " ":
                if self.tabela_jogo[c][1] == "X":
                    preferencia.append([c, 0])
                possibilidades.append([c, 0])
        
        # vertical
        for c in range(0, 3):
            if self.tabela_jogo[0][c] == self.tabela_jogo[1][c] and \
                self.tabela_jogo[0][c] != " " and self.tabela_jogo[2][c] == " ":
                if self.tabela_jogo[0][c] == "X":
                    preferencia.append([2, c])
                possibilidades.append([2, c])

            if self.tabela_jogo[0][c] == self.tabela_jogo[2][c] and \
                self.tabela_jogo[0][c] != " " and self.tabela_jogo[0][c] == " ":
                if self.tabela_jogo[0][c] == "X":
                    preferencia.append([1, c])
                possibilidades.append([1, c])

            if self.tabela_jogo[1][c] == self.tabela_jogo [2][c] and \
                self.tabela_jogo[1][c] != " " and self.tabela_jogo[0][c] == " ":
                if self.tabela_jogo[1][c] == "X":
                    preferencia.append([0, c])
                possibilidades.append([0, c])

        # diagonal 1
        if self.tabela_jogo[0][0] == self.tabela_jogo[1][1] and \
            self.tabela_jogo[1][1] != " " and self.tabela_jogo[2][2] == " ":
            if self.tabela_jogo[0][0] == "X":
                preferencia.append([2, 2])
            possibilidades.append([2, 2])

        if self.tabela_jogo[0][0] == self.tabela_jogo[2][2] and \
            self.tabela_jogo[0][0] != " " and self.tabela_jogo[1][1] == " ":
            if self.tabela_jogo[0][0] == "X":
                preferencia.append([1, 1])
            possibilidades.append([1, 1])

        if self.tabela_jogo[1][1] == self.tabela_jogo[2][2] and \
            self.tabela_jogo[2][2] != " " and self.tabela_jogo[0][0] == " ":
            if self.tabela_jogo[1][1] == "X":
                preferencia.append([0, 0])
            possibilidades.append([0, 0])

        # diagonal 2
        if self.tabela_jogo[0][2] == self.tabela_jogo[1][1] and \
            self.tabela_jogo[1][1] != " " and self.tabela_jogo[2][0] == " ":
            if self.tabela_jogo[0][2] == "X":
                preferencia.append([2, 0])
            possibilidades.append([2, 0])

        if self.tabela_jogo[0][2] == self.tabela_jogo[2][0] and \
            self.tabela_jogo[2][0] != " " and self.tabela_jogo[1][1] == " ":
            if self.tabela_jogo[0][2] == "X":
                preferencia.append([1, 1])
            possibilidades.append([1, 1])
            
        if self.tabela_jogo[1][1] == self.tabela_jogo[2][0] and \
            self.tabela_jogo[2][0] != " " and self.tabela_jogo[0][2] == " ":
            if self.tabela_jogo[1][1] == "X":
                preferencia.append([0, 2])
            possibilidades.append([0, 2])

        if len(possibilidades) == len(preferencia) == 0:
            aleatorio_linha = randint(0, 2)
            aleatorio_coluna = randint(0, 2)
            while self.tabela_jogo[aleatorio_linha][aleatorio_coluna] != " ":
                aleatorio_linha = randint(0, 2)
                aleatorio_coluna = randint(0, 2)
            return (aleatorio_linha, aleatorio_coluna)
        
        if len(preferencia) > 0:
            return (preferencia[0][0], preferencia[0][1])
        
        return (possibilidades[0][0], possibilidades[0][1])

    def checar_vitoria(self, jogador):
        # horizontal
        for linha in self.tabela_jogo:
            if linha[0] == linha[1] == linha[2] == jogador:
                return True

        # vertical
        for i in range(0, 3):
            if self.tabela_jogo[0][i] == self.tabela_jogo[1][i] == self.tabela_jogo[2][i] == jogador:
                return True

        # diagonal
        if (self.tabela_jogo[0][0] == self.tabela_jogo[1][1] == self.tabela_jogo[2][2] == jogador) \
            or \
            (self.tabela_jogo[0][2] == self.tabela_jogo[1][1] == self.tabela_jogo[2][0] == jogador):
            return True

        return False
