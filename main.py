import disnake
from entidades.Eery import Eery
from save_and_load import *


intents = disnake.Intents.all()
bot = Eery(command_prefix="!", intents=intents)

@bot.before_slash_command_invoke
async def before_slash_command_invoke(inter : disnake.ApplicationCommandInteraction):
    bot.usuario_servico.registrar(inter.user)

key = carregar("keys")["key"]
bot.run(key)
