from PIL import Image
from disnake import Emoji


class Carta():
    def __init__(self, simbolo : str, cor : str | None = None, emoji : Emoji = None):
        self.cor = cor if cor != None else "especial"
        self.simbolo = simbolo
        self.especial = cor == None
        self.emoji = emoji
        self.imagem = Image.open(f"comandos/jogos/Uno/imagens/{self.cor}_{self.simbolo}.png").convert("RGBA")
        