from disnake.ext import commands

from servicos.UsuarioServico import UsuarioServico


class EeryType(commands.Bot):
    xp_adicionado : list
    usuario_servico : UsuarioServico
    configs : dict
    valor_canais_xp : dict