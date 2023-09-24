import asyncio
import disnake
from disnake.ext import commands
import requests
from entidades.Eery import Eery
from entidades.Usuario import Usuario
from save_and_load import carregar


class Twitch(commands.Cog):
    def __init__(self, bot : Eery):
        self.bot = bot
        self.usuario_servico = bot.usuario_servico
        
        self.pessoas_em_live = []
        
        twitch_keys = carregar("keys")["twitch_keys"]
        self.twitch_bot_id = twitch_keys["twitch_bot_id"]
        self.twitch_bot_secret = twitch_keys["twitch_bot_secret"]
        
        self.token_url = "https://id.twitch.tv/oauth2/token"
        self.token_params = {
            "client_id": self.twitch_bot_id,
            "client_secret": self.twitch_bot_secret,
            "grant_type": "client_credentials"
        }

    @commands.slash_command(name="twitch", description="Registra seu nome de usuário da Twitch (Notifica quando você abrir live)")
    async def twitch(self, inter : disnake.ApplicationCommandInteraction, nome_usuario : str):
        await inter.response.defer()
        
        usuario = self.usuario_servico.pegar_usuario(inter.user)
        usuario.twitch = nome_usuario.strip()
        self.usuario_servico.salvar_usuario(usuario)
        
        await inter.edit_original_message("Twitch atualizada com sucesso!")
        
    async def check_twitch_stream(self):
        while True:
            usuarios = self.usuario_servico.pegar_todos_usuarios()
            
            response = requests.post(self.token_url, params=self.token_params)
            data = response.json()
            access_token = data["access_token"]
            headers = {
                "Client-ID": self.twitch_bot_id,
                "Authorization": f"Bearer {access_token}"
            }
            
            for usuario in usuarios:
                await self.twitch_mensagem_live(usuario, headers)
                
            await asyncio.sleep(10)

    async def twitch_mensagem_live(self, usuario : Usuario, headers : dict):
        if usuario.twitch == None:
            return
        
        response = requests.get(
            f"https://api.twitch.tv/helix/streams?user_login={usuario.twitch}",
            headers=headers
        )
        data = response.json()
        try:
            if data["data"] != []:
                if data["data"][0]["type"] != "live" or usuario.id in self.pessoas_em_live:
                    return
                self.pessoas_em_live.append(usuario.id)
                canal_divulgacao = self.bot.get_channel(self.bot.configs["canais"]["divulgacao"])
                await canal_divulgacao.send(f"<@{usuario.id}> está ao vivo na Twitch! Assista em https://www.twitch.tv/{usuario.twitch}")
            
            elif usuario.id in self.pessoas_em_live:
                self.pessoas_em_live.remove(usuario.id)
        except:
            pass
        
        
def setup(bot: Eery):
    bot.add_cog(Twitch(bot))
    