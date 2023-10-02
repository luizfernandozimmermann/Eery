import io
from math import ceil
import disnake
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from comandos.xp_funcoes import obter_level
from entidades.EeryType import EeryType
from entidades.Usuario import Usuario
from save_and_load import carregar



def criar_imagem_xp(usuario : Usuario, pos_ranking : int) -> Image.Image:
    level, xp, xp_requerido = obter_level(usuario.xp)
    
    imagem = Image.new("RGBA", (934, 282))
    draw = ImageDraw.Draw(imagem)
    draw.rounded_rectangle(((0, 0), (934, 282)), 10, "#23272a")
    draw.rounded_rectangle(((24, 36), (909, 245)), 10, "#090a0b")
    
    avatar = requests.get(usuario.display_avatar.url, stream = True).raw
    avatar = Image.open(avatar).convert("RGBA").resize((160, 160))
    
    def imagem_circular(imagem_circular : Image.Image):
        width, height = imagem_circular.size
        x = (width - height)//2
        imagem_circular = imagem_circular.crop((x, 0, x+height, height))

        mask = Image.new('L', imagem_circular.size)
        mask_draw = ImageDraw.Draw(mask)
        width, height = imagem_circular.size
        mask_draw.ellipse((0, 0, width, height), fill=255)

        imagem_circular.putalpha(mask)
        return imagem_circular
        
    avatar = imagem_circular(avatar)
    imagem.paste(avatar, (42, 62), avatar)
    
    def adicionar_barra_xp():
        x = 258
        y = 184
        width = 596
        height = 35
        
        draw.rectangle((x + (height / 2), y, x + width + (height / 2), y + height), fill="#484b4e", width=10)
        draw.ellipse((x + width, y, x + height + width, y + height), fill="#484b4e")
        draw.ellipse((x, y, x + height, y + height), fill="#484b4e")
        
        width = int(width*(xp / xp_requerido))
        draw.rectangle((x + (height / 2), y, x + width + (height / 2), y + height), fill="#62d3f5", width=10)
        draw.ellipse((x + width, y, x + height + width, y + height), fill="#62d3f5")
        draw.ellipse((x, y, x + height, y + height), fill="#62d3f5")

    adicionar_barra_xp()
    
    # textos
    fonte_52 = ImageFont.truetype("open_sans.ttf", size = 52)
    fonte_36 = ImageFont.truetype("open_sans.ttf", size = 36)
    fonte_25 = ImageFont.truetype("open_sans.ttf", size = 25)
    
    draw.text((274, 127), usuario.name, "#FFFFFF", font=fonte_36)
    
    # xp / xp_requerido
    def formatar_xp(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
    xp = formatar_xp(xp)
    xp_requerido = formatar_xp(xp_requerido)
    
    largura_texto = fonte_25.getmask(f"/ {xp_requerido} XP").getbbox()[2]
    pos_x = 882 - largura_texto
    draw.text((pos_x, 139), f"/ {xp_requerido} XP", "#7f8384", font=fonte_25)
    pos_x -= fonte_25.getmask(f"{xp}").getbbox()[2] + 9
    draw.text((pos_x, 139), f"{xp} ", "#FFFFFF", font=fonte_25)
    
    # LEVEL {level}
    largura_texto = fonte_52.getmask(f"{level}").getbbox()[2]
    pos_x = 878 - largura_texto
    draw.text((pos_x, 55), f"{level}", "#62d3f5", font=fonte_52)
    
    largura_texto = fonte_25.getmask(f"LEVEL").getbbox()[2]
    pos_x -= largura_texto
    draw.text((pos_x, 82), "LEVEL", "#62d3f5", font=fonte_25)
    pos_x -= 20
    
    # RANK #{rank}
    largura_texto = fonte_52.getmask(f"#{pos_ranking}").getbbox()[2]
    pos_x -= largura_texto
    draw.text((pos_x, 55), f"#{pos_ranking}", "#FFFFFF", font=fonte_52)
    pos_x -= 9
    
    largura_texto = fonte_25.getmask(f"RANK").getbbox()[2]
    pos_x -= largura_texto
    draw.text((pos_x, 82), f"RANK", "#FFFFFF", font=fonte_25)
    
    return imagem


class Xp(commands.Cog):
    def __init__(self, bot : EeryType):
        self.bot = bot
        self.usuario_servico = bot.usuario_servico
            
    @commands.slash_command(name="valores_xp", description="Veja a quantidade de xp que cada canal dá!")
    async def valores_xp(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        embed = disnake.Embed(
            title="Valores de xp para cada canal",
            colour=disnake.Colour.blue()
        )
        valor_canais_xp = carregar("valor_canais_xp")
        valor_canais_xp = dict(sorted(valor_canais_xp.items(), key=lambda item: item[1]))
        
        for valor, canais in valor_canais_xp.items():
            canais_field = []
            for canal in canais:
                if self.bot.get_channel(canal).guild == inter.guild:
                    canais_field.append(f"<#{canal}>")
            
            if len(canais_field) != 0:
                embed.add_field(
                    name=f"{valor}x de xp",
                    value=", ".join(canais_field)
                )
        
        embed.set_footer(text="Os canais que não foram mencionados tem 1.0x de xp.")
        
        await inter.edit_original_message(embed=embed)
    
    @commands.slash_command(name="level", description="Veja seu XP")
    async def level(self, inter : disnake.ApplicationCommandInteraction, usuario : disnake.User = None):
        await inter.response.defer()
        
        usuario = self.usuario_servico.pegar_usuario_valido(inter.user, usuario)
        
        usuarios = self.usuario_servico.pegar_todos_usuarios()
        
        posicao_ranking = sorted(usuarios, key=lambda x: -x.xp).index(usuario) + 1
        
        imagem = criar_imagem_xp(usuario, posicao_ranking)
        with io.BytesIO() as image_binary:
            imagem.save(image_binary, 'PNG')
            image_binary.seek(0)
            await inter.edit_original_message(file=disnake.File(fp=image_binary, filename='image.png'))

    @commands.slash_command(name="ranking", description="Veja a tabela de ranking de xp do server")
    async def ranking(self, inter : disnake.ApplicationCommandInteraction, pagina : int = 1):
        await inter.response.defer()
        
        usuarios = self.usuario_servico.pegar_todos_usuarios()
        view = self.RankingView(self.bot, usuarios, pagina)
        
        await inter.edit_original_message(embed=view.montar_embed(), view=view, file=view.imagem)
    
    
    class RankingView(disnake.ui.View):
        def __init__(self, bot : EeryType, usuarios : list[Usuario], pagina : int):
            super().__init__(timeout=None)
            self.bot = bot
            
            self.lista_ordenada = sorted(usuarios, key=lambda usuario: -usuario.xp)
            self.quantidade_por_pagina = 5
            self.maximo_paginas = ceil(len(self.lista_ordenada) / self.quantidade_por_pagina)
            
            self.pagina = pagina
            if self.pagina > self.maximo_paginas or self.pagina < 1:
                self.pagina = 1
                
            self.usuarios = usuarios
                            
        def montar_embed(self):
            embed = disnake.Embed(
                title=f"Ranking de XP do server - {self.pagina}/{self.maximo_paginas}",
                colour=disnake.Colour.blue()
            )
            self.montar_imagem()
            embed.set_image("attachment://image.png")
            return embed
            
        def montar_imagem(self):
            self.imagem = Image.new("RGBA", (934, self.quantidade_por_pagina * 282))
            pos_y = 0
            for i in range((self.pagina - 1)* self.quantidade_por_pagina, self.pagina * self.quantidade_por_pagina):
                usuario = self.lista_ordenada[i]
                xp = self.lista_ordenada[i].xp
                
                imagem_usuario = criar_imagem_xp(usuario, i + 1)
                self.imagem.paste(imagem_usuario, (0, pos_y))
                pos_y += 282
            
            with io.BytesIO() as imagem:
                self.imagem.save(imagem, 'PNG')
                imagem.seek(0)
                self.imagem = disnake.File(fp=imagem, filename='image.png')
            
        @disnake.ui.button(label="<", style=disnake.ButtonStyle.blurple, disabled=True)
        async def pagina_anterior(self, button : disnake.ui.Button, inter : disnake.MessageInteraction):
            await inter.response.defer()
            self.pagina -= 1
            
            self.pagina_posterior.disabled = False
            if self.pagina == 1:
                self.pagina_anterior.disabled = True
            
            await inter.edit_original_message(embed=self.montar_embed(), view=self, file=self.imagem)
        
        @disnake.ui.button(label=">", style=disnake.ButtonStyle.blurple)
        async def pagina_posterior(self, button : disnake.ui.Button, inter : disnake.MessageInteraction):
            await inter.response.defer()
            
            self.pagina += 1
            
            self.pagina_anterior.disabled = False
            if self.pagina == self.maximo_paginas:
                self.pagina_posterior.disabled = True
            
            await inter.edit_original_message(embed=self.montar_embed(), view=self, file=self.imagem)
