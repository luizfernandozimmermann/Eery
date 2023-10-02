import disnake

from comandos.jogos.JogoVelha.JogoVelhaJogador import JogoVelhaJogador
from comandos.jogos.JogoVelha.JogoVelhaMapa import JogoVelhaMapa


class JogoVelha(disnake.ui.View):
    def __init__(self, author : disnake.User):
        super().__init__()
        self.jogo_mapa = JogoVelhaMapa()
        self.jogador = JogoVelhaJogador(author.name, author.id)
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
            description = "Jogador: X, Eery: O",
            colour=disnake.Colour.blue()
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
