from PIL import Image


class Carta():
    def __init__(self, simbolo : str, cor : str | None = None):
        self.cor = cor if cor != None else "especial"
        self.simbolo = simbolo
        self.especial = cor == None or not simbolo.isnumeric()
        self.imagem = Image.open(f"comandos/jogos/Uno/imagens/{self.cor}_{self.simbolo}.png").convert("RGBA")
        