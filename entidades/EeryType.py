from disnake.ext import commands

from servicos.UsuarioServico import UsuarioServico


class EeryType(commands.Bot):
    def __init__(self):
        self.xp_adicionado : list
        self.usuario_servico : UsuarioServico
        self.configs : dict
        self.valor_canais_xp : dict