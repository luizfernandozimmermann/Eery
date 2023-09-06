import asyncio
import disnake
from disnake.ext import commands
import requests
from save_and_load import *


class Twitch(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client
        
        self.pessoas_em_live = []
        
        twitch_keys = carregar("keys")["twitch_keys"]
        self.twitch_client_id = twitch_keys["twitch_client_id"]
        self.twitch_client_secret = twitch_keys["twitch_client_secret"]
        
        self.token_url = "https://id.twitch.tv/oauth2/token"
        self.token_params = {
            "client_id": self.twitch_client_id,
            "client_secret": self.twitch_client_secret,
            "grant_type": "client_credentials"
        }
        
        client.loop.create_task(self.check_twitch_stream())

    @commands.slash_command(name="twitch", description="Registra seu nome de usuário da Twitch (Notifica quando você abrir live)")
    async def twitch(inter : disnake.ApplicationCommandInteraction, nome_usuario : str):
        await inter.response.defer()
        membros = carregar()
        membros[str(inter.author.id)]["twitch"] = nome_usuario
        salvar(membros)
        await inter.edit_original_message("Twitch atualizada com sucesso!")
        
    async def check_twitch_stream(self):
        while True:
            membros = carregar()
            
            response = requests.post(self.token_url, params=self.token_params)
            data = response.json()
            access_token = data["access_token"]
            headers = {
                "Client-ID": self.twitch_client_id,
                "Authorization": f"Bearer {access_token}"
            }
            
            for id_membro, membro in membros.items():
                await self.twitch_mensagem_live(id_membro, membro, headers)
                
            await asyncio.sleep(60)

    async def twitch_mensagem_live(self, id_membro : int, membro : dict, headers : dict):
        if membro["twitch"] == "Não informado":
            return
        
        twitch_streamer = membro["twitch"]
        response = requests.get(
            f"https://api.twitch.tv/helix/streams?user_login={twitch_streamer}",
            headers=headers
        )
        data = response.json()
        
        if data["data"] != []:
            if data["data"][0]["type"] != "live" or str(id_membro) in self.pessoas_em_live:
                return
            self.pessoas_em_live.append(str(id_membro))
            await self.client.channel_geral.send(f"<@{id_membro}> está ao vivo na Twitch! Assista em https://www.twitch.tv/{twitch_streamer}")
        
        elif str(id_membro) in self.pessoas_em_live:
            self.pessoas_em_live.remove(str(id_membro))
        
        
def setup(client: commands.Bot):
    client.add_cog(Twitch(client))
    