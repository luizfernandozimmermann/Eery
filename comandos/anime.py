from bs4 import BeautifulSoup
import disnake
from disnake.ext import commands
import requests
from save_and_load import *
from urllib.request import urlopen


class Anime(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    def salvar_animes(self, lista_animes : dict, id_usuario : int):
        membros = carregar()
        membros[str(id_usuario)]["animes"] = lista_animes
        salvar(membros)
    
    @commands.slash_command(name="anime", description="Mostra lista de animes (ou de episódios do anime dito)")
    async def anime(self, inter : disnake.ApplicationCommandInteraction, 
                    anime : str = None, episodio : int = None) :
        await inter.response.defer(ephemeral=True)
        
        anime_view = self.AnimeView(anime, inter.user, episodio)
        
        if anime != None:
            anime = anime.strip()
            anime_formatado = anime.lower().replace(' ', '-')
            if episodio != None:
                if requests.get(f"https://goyabu.org/animes/{anime_formatado}/{episodio}").status_code != 200:
                    await inter.edit_original_message("Não foi possível achar este anime/episódio.")
                    return
        
            response = requests.get(f"https://goyabu.org/animes/{anime_formatado}-todos-os-episodios")
            if response.status_code == 200:
                self.salvar_animes(
                    id_usuario=inter.user.id,
                    lista_animes=anime_view.lista_animes
                )
                
                await inter.edit_original_message(view=anime_view, embed=anime_view.embed)
                return
            
            await inter.edit_original_message("Não consegui encontrar o anime :(")
            return
                 
        await inter.edit_original_message(view=anime_view, embed=anime_view.embed)
    
    class AnimeView(disnake.ui.View):
        def __init__(self, anime : str, usuario : disnake.User | disnake.Member, episodio : int):
            super().__init__()
            self.timeout = 1800
            self.USUARIO = usuario
            
            self.anime = anime
            if anime != None:
                self.anime_formatado = self.anime.lower().replace(' ', '-')
            self.episodio = episodio
            self.lista_animes : dict = carregar()[str(self.USUARIO.id)]["animes"]
            
            if self.anime == None:
                self.pagina = 1
                
                if self.pagina * 8 >= len(self.lista_animes):
                    self.botao_proximo_lista.disabled = True
                    
                self.atualizar_embed(titulo=f"Lista de animes - Página {self.pagina}", footer="Para adicionar um anime para sua lista, basta utilizar /anime <nome_do_anime>")
                self.carregar_lista_animes_embed()
                
            else:
                if self.episodio == None:
                    if anime not in self.lista_animes:
                        self.lista_animes[anime] = {
                            "episodio": 1
                        }
                    self.episodio = self.lista_animes[anime]["episodio"]
                
                self.remove_item(self.botao_anterior_lista)
                self.remove_item(self.botao_proximo_lista)
                
                if requests.get(f"https://goyabu.org/animes/{self.anime_formatado}/{self.episodio - 1}").status_code == 200:
                    self.botao_anterior_episodio.disabled = False
                if requests.get(f"https://goyabu.org/animes/{self.anime_formatado}/{self.episodio + 1}").status_code == 200:
                    self.botao_proximo_episodio.disabled = False
                
                self.atualizar_embed(titulo=f"{self.anime.title()} - Episódio {self.episodio}", 
                                     player=self.pegar_url_video())
              
        def pegar_url_video(self):
            response = requests.get(f"https://goyabu.org/animes/{self.anime_formatado}/{self.episodio}")
            soup = BeautifulSoup(response.text, "html.parser")
            video_tag = soup.find("video")

            if video_tag:
                src = video_tag.get("src")
                return src
                        
        def atualizar_embed(self, titulo : str, descricao : str = "", player : str = None, footer : str = None):
            self.embed = disnake.Embed(
                title=titulo,
                description=descricao if player == None else f"{descricao} [Link para o episódio]({player})"
            )
            if footer != None:
                self.embed.set_footer(text=footer)

        def carregar_lista_animes_embed(self):
            lista_animes = dict(sorted(self.lista_animes.items())[(self.pagina - 1) * 8:])
            itens_adicionados = 0
            for anime, temporadas_episodios in lista_animes.items():
                self.embed.add_field(
                    name = anime.title(), 
                    value = f"Episódio: {temporadas_episodios['episodio']}",
                    inline = False
                )
                itens_adicionados += 1
                if itens_adicionados == 8:
                    return
                
        async def atualizar_mensagem(self, inter : disnake.ApplicationCommandInteraction):
            await inter.response.edit_message(view=self, embed=self.embed)

        @disnake.ui.button(label="<", style=disnake.ButtonStyle.blurple, disabled=True)
        async def botao_anterior_lista(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
            self.pagina -= 1
            self.atualizar_embed(titulo=f"Lista de animes - Página {self.pagina}", footer="Para adicionar um anime para sua lista, basta utilizar /anime <nome_do_anime>")
            self.carregar_lista_animes_embed()
            
            if self.pagina * 8 > len(self.lista_animes):
                self.botao_proximo_lista.disabled = False
                
            self.botao_anterior_lista.disabled = False
            if self.pagina == 1:
                self.botao_anterior_lista.disabled = True
                
            await self.atualizar_mensagem(inter)
            
        @disnake.ui.button(label=">", style=disnake.ButtonStyle.blurple)
        async def botao_proximo_lista(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
            self.pagina += 1
            self.atualizar_embed(titulo=f"Lista de animes - Página {self.pagina}", footer="Para adicionar um anime para sua lista, basta utilizar /anime <nome_do_anime>")
            self.carregar_lista_animes_embed()
            
            self.botao_anterior_lista.disabled = False
            
            self.botao_proximo_lista.disabled = False
            if self.pagina * 8 >= len(self.lista_animes):
                self.botao_proximo_lista.disabled = True
                
            await self.atualizar_mensagem(inter)


        @disnake.ui.button(label="<", style=disnake.ButtonStyle.blurple, disabled=True)
        async def botao_anterior_episodio(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
            self.episodio -= 1
            self.botao_proximo_episodio.disabled = False
            
            if requests.get(f"https://goyabu.org/animes/{self.anime_formatado}/{self.episodio - 1}").status_code != 200:
                self.botao_anterior_episodio.disabled = True
            self.atualizar_embed(titulo=f"{self.anime.title()} - Episódio {self.episodio}", player=self.pegar_url_video())
            
            membros = carregar()
            membros[str(inter.user.id)]["animes"][self.anime]["episodio"] = self.episodio
            salvar(membros)
            
            await inter.response.edit_message(view=self, embed=self.embed)
        
        @disnake.ui.button(label=">", style=disnake.ButtonStyle.blurple, disabled=True)
        async def botao_proximo_episodio(self, button: disnake.ui.Button, inter: disnake.ApplicationCommandInteraction):
            self.episodio += 1
            self.botao_anterior_episodio.disabled = False
            
            if requests.get(f"https://goyabu.org/animes/{self.anime_formatado}/{self.episodio + 1}").status_code != 200:
                self.botao_proximo_episodio.disabled = True
            self.atualizar_embed(titulo=f"{self.anime.title()} - Episódio {self.episodio}", player=self.pegar_url_video())
            
            membros = carregar()
            membros[str(inter.user.id)]["animes"][self.anime]["episodio"] = self.episodio
            salvar(membros)
            
            await inter.response.edit_message(view=self, embed=self.embed)
        

def setup(client: commands.Bot):
    client.add_cog(Anime(client))
