import io
from PIL import Image
import disnake
from disnake.ext import commands
from random import randint


class JogoVelha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="jogar", description="Jogo da velha :)")
    async def jogar(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        view = self.JogoVelhaView(inter.author)
        embed = view.gerar_embed(inter.author.name)
        await inter.edit_original_message(embed=embed, view=view, file=view.jogo_mapa.gerar_mapa())


    class JogoVelhaView(disnake.ui.View):
        def __init__(self, author : disnake.User):
            super().__init__()
            self.jogo_mapa = self.Jogo_velha_mapa()
            self.jogador = self.Jogo_velha_jogador(author.name, author.id)
            self.botoes_funcoes = [self.botao1, 
                                   self.botao2, 
                                   self.botao3, 
                                   self.botao4, 
                                   self.botao5, 
                                   self.botao6, 
                                   self.botao7, 
                                   self.botao8, 
                                   self.botao9]

        def gerar_embed(self, nome_jogador, resultado = ""):
            embed = disnake.Embed(
                title=f"Jogo da Velha com {nome_jogador} {resultado}",
                description = "Jogador: X, Eery: O"
                )
            embed.set_image("attachment://image.png")
            return embed
        
        async def botao(self, 
                        button : disnake.ui.Button, 
                        inter : disnake.ApplicationCommandInteraction,
                        linha, coluna):
            if self.jogo_mapa.finalizado or self.jogador.id_jogador != inter.author.id:
                return

            self.jogo_mapa.jogar(linha, coluna, self.jogador.letra)
            self.botoes_funcoes[linha * 3 + coluna].disabled = True

            resultado = ""
            if self.jogo_mapa.checar_vitoria(self.jogador.letra):
                resultado += "Vitória do jogador!"

            elif self.jogo_mapa.contagem == 9:
                resultado += "Empate!"
                self.jogo_mapa.finalizado = True

            else:
                jogada_bot_linha, jogada_bot_coluna = self.jogo_mapa.jogada_bot()
                
                self.jogo_mapa.jogar(jogada_bot_linha, jogada_bot_coluna, "O")
                self.botoes_funcoes[jogada_bot_linha * 3 + jogada_bot_coluna].disabled = True

                if self.jogo_mapa.checar_vitoria("O"):
                    resultado += "Vitória minha!"

            embed = self.gerar_embed(self.jogador.nome, resultado)
            await inter.response.edit_message(embed=embed, view=self, file=self.jogo_mapa.gerar_mapa())
            
        @disnake.ui.button(label="1", style=disnake.ButtonStyle.blurple)
        async def botao1(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 0, 0)
        
        @disnake.ui.button(label="2", style=disnake.ButtonStyle.blurple)
        async def botao2(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 0, 1)

        @disnake.ui.button(label="3", style=disnake.ButtonStyle.blurple)
        async def botao3(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 0, 2)

        @disnake.ui.button(label="4", style=disnake.ButtonStyle.blurple)
        async def botao4(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 1, 0)

        @disnake.ui.button(label="5", style=disnake.ButtonStyle.blurple)
        async def botao5(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 1, 1)

        @disnake.ui.button(label="6", style=disnake.ButtonStyle.blurple)
        async def botao6(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 1, 2)

        @disnake.ui.button(label="7", style=disnake.ButtonStyle.blurple)
        async def botao7(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 2, 0)

        @disnake.ui.button(label="8", style=disnake.ButtonStyle.blurple)
        async def botao8(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 2, 1)

        @disnake.ui.button(label="9", style=disnake.ButtonStyle.blurple)
        async def botao9(self, button : disnake.ui.Button, inter : disnake.ApplicationCommandInteraction):
            await self.botao(button, inter, 2, 2)


        class Jogo_velha_jogador():
            letra = "X"
            def __init__(self, nome_jogador : str , id_jogador : int):
                self.nome = nome_jogador
                self.id_jogador = id_jogador


        class Jogo_velha_mapa():
            def __init__(self):
                self.contagem = 0
                self.tabela_jogo = [[" ", " ", " "],
                            [" ", " ", " "],
                            [" ", " ", " "]]
                
                self.imagem_mapa = Image.open("comandos/imagens_jogos/jogo_velha/fundo.png")
                self.finalizado = False

            def jogar(self, linha : int, coluna : int, letra : str):
                self.contagem += 1
                self.tabela_jogo[linha][coluna] = letra
                imagem_letra = Image.open(f"comandos/imagens_jogos/jogo_velha/player_{letra.lower()}.png")
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
         

def setup(bot: commands.Bot):
    bot.add_cog(JogoVelha(bot))
