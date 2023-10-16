import codecs
from datetime import datetime, timezone
from random import randint
import re
import disnake
from disnake.ext import commands, tasks
from comandos.Adm import Adm
from comandos.Comandos import Comandos
from comandos.Jogos import Jogos
from comandos.Perfil import Perfil
from comandos.Twitch import Twitch
from comandos.Xp import Xp
from comandos.xp_funcoes import obter_level
from entidades.EeryType import EeryType
from save_and_load import carregar

from servicos.UsuarioServico import UsuarioServico


class Eery(EeryType):
    def __init__(self, command_prefix : str, intents : disnake.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.xp_adicionado = []
        
        self.usuario_servico = UsuarioServico(self)
        self.configs = carregar("configs")
        self.valor_canais_xp = carregar("valor_canais_xp")
        self.remove_command("help")
        self.add_cog(Adm(self))
        self.add_cog(Comandos(self))
        self.add_cog(Jogos(self))
        self.add_cog(Perfil(self))
        self.add_cog(Twitch(self))
        self.add_cog(Xp(self))
       
    @tasks.loop(seconds=59)
    async def loop_1m(self):
        self.xp_adicionado = []
        
        horario = datetime.now(timezone.utc)
        minuto = horario.minute
        hora = horario.hour - 3
        if hora < 0:
            hora = 24 + hora
        
        if minuto == 00:
            numero_aleatorio = randint(0,4)
            if hora == 7:
                imagens_link = [
                    "https://cdn.discordapp.com/attachments/1054167826937688067/1055609966997811251/bomdia_1.webp",
                    "https://cdn.discordapp.com/attachments/1054167826937688067/1055609967513698434/bomdia_2.jpg",
                    "https://cdn.discordapp.com/attachments/1054167826937688067/1055609967811506245/bomdia_3.webp",
                    "https://cdn.discordapp.com/attachments/1054167826937688067/1055609968230932620/bomdia_4.jpg",
                    "https://cdn.discordapp.com/attachments/1054167826937688067/1055609966804860948/bomdia_5.jpg"
                ]
                await self.channel_geral.send(f"[Bom dia!!!]({imagens_link[numero_aleatorio]})")
            
            elif hora == 13:
                imagens_link = [
                    "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/mensagens-de-boa-tarde-ka0z3-fxl.jpg?w=1200&ssl=1",
                    "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/8edfee13bbfe582be562c0caec2559d4-cute-kittens-funny-dogs.jpg?w=540&ssl=1",
                    "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/69ac6533cbd5e546bea791a1aec4486b-nadir-pasta.jpg?w=511&ssl=1",
                    "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/179.jpg?w=632&ssl=1",
                    "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/2016-Abril-28-Boa-tarde-IMG-2.jpg?w=720&ssl=1"
                ]
                await self.channel_geral.send(f"[Boa tarde!]({imagens_link[numero_aleatorio]})")

            elif hora == 19:
                imagens_link = [
                    "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2022/09/imagem-de-boa-noite.png?resize=768%2C798&ssl=1",
                    "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Boa-noite-a-todos.jpg?w=360&ssl=1",
                    "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Que-Deus-abencoe-a-sua-noite-e-te-der-lindos-sonhos.jpg?w=480&ssl=1",
                    "https://i.pinimg.com/564x/12/d1/cc/12d1cc49b307e23f6cab2d9bd07bd670.jpg",
                    "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2021/12/Boa-noite-Nada-e-dificil-quando-temos-fe-em-Deus-e-na-vida.jpg?w=700&ssl=1"
                ]
                await self.channel_geral.send(f"[Boa noite!!!]({imagens_link[numero_aleatorio]})")

            elif hora == 0:
                dia = datetime.now(timezone.utc)
                mes = '%02d' % dia.month
                dia = '%02d' % dia.day
                usuarios = self.usuario_servico.pegar_todos_usuarios()
                for usuario in usuarios:
                    if usuario.aniversario == dia + "/" + mes:
                        await self.channel_geral.send("<@" + usuario.id + "> FELIZ ANIVERSÁRIO!!!\nhttps://media.discordapp.net/attachments/842921629054271518/1050245621954641950/happy_birthday.mp4")
                        break

            elif hora == 1:
                online = len([usuario for usuario in self.usuario_servico.pegar_todos_usuarios() if usuario.status != disnake.Status.online])
                if online >= self.channel_geral.guild.member_count // 2:
                    await self.channel_geral.send(file="[BORA DORMIR CAMBADA](https://imgb.ifunny.co/videos/576571deca32576c87db6b09e14f2b893d2b28818cff93c17826a9590dd5cf34_1.mp4)")

    async def on_slash_command_error(self, interaction : disnake.ApplicationCommandInteraction, 
                                    exception : commands.CommandError):
        try:
            await interaction.response.defer()
        except:
            pass
        
        await self.owner.send(f"## Ocorreu um erro: " +
                                f"\n- Servidor: **{interaction.guild.name}**" +
                                f"\n- Canal: **{interaction.channel.name}** às **{datetime.now().strftime('%H:%M:%S, %Y/%m/%d')}**" + 
                                f"\n- Usuário: **{interaction.user.name}**" + 
                                f"\n- Comando: **{interaction.application_command.name}**" +
                                f"\n- Exceção: \n```{exception}```")
        
        await interaction.edit_original_message("Ocorreu um erro :(")

    async def on_ready(self):
        self.loop_1m.start()
        
        self.channel_geral = self.get_channel(self.configs["canais"]["geral"])
        self.canal_lvl_up = self.get_channel(self.configs["canais"]["xp"])
        self.loop.create_task(self.cogs["Twitch"].check_twitch_stream())

    async def on_message(self, message : disnake.message.Message):
        if not message.author.bot and message.guild.id == self.canal_lvl_up.guild.id:
            if self.configs["xp"]["ativo"] and message.author.id not in self.xp_adicionado:
                usuario = self.usuario_servico.pegar_usuario(message.author)
                
                valor_xp = 0
                for valor_canal, lista_canais in self.valor_canais_xp.items():
                    if valor_xp < float(valor_canal):
                        if message.channel.id in lista_canais:
                            valor_xp = float(valor_canal)
                valor_xp = 1 if valor_xp == 0 else valor_xp
                xp = usuario.xp
            
                lvl_anterior = obter_level(xp)[0]
                xp += randint(int(15 * valor_xp), int(25 * valor_xp)) * self.configs["xp"]["multiplicador"]
                lvl_posterior = obter_level(xp)[0]
                
                usuario.xp = xp
                if lvl_anterior != lvl_posterior:
                    await self.canal_lvl_up.send(f"<@{message.author.id}> acaba de upar para o level {lvl_posterior}!")
                
                self.usuario_servico.salvar_usuario(usuario)
                
                self.xp_adicionado.append(message.author.id)
            
            if self.user.mentioned_in(message):
                data = datetime.now(timezone.utc)
                hora = data.hour - 3
                autor = message.author.id

                if 7 <= hora < 13 and "bom dia" in message.content.lower():
                    await message.reply("<@" + str(autor) + "> Bom dia !!!")
                elif 13 <= hora < 19 and "boa tarde" in message.content.lower():
                    await message.reply("<@" + str(autor) + "> Boa tarde !!!")
                elif "boa noite" in message.content.lower():
                    await message.reply("<@" + str(autor) + "> Boa noite !!!")

                if "feliz ano novo" in message.content.lower():
                    await message.reply("<@" + str(autor) + "> Feliz ano novo para você !!! Espero que você tenha um ótimo 2012!!!")
            
            if f"<@{self.user.id}> <@{self.user.id}>" in message.content:
                await message.channel.send(":p")
            
            reacoes = self.configs["reacoes"]
            
            for chave, reacao in reacoes.items():
                if chave in message.content.lower():
                    try:
                        reacao = codecs.decode(reacao, 'unicode_escape')
                    except:
                        pass
                    await message.add_reaction(f"{reacao}")
            
            # vxtwitter
            matches_twitter = re.match(r"(https://twitter.com/.*?/status/\w*)", message.content)
            matches_x = re.match(r"(https://x.com/.*?/status/\w*)", message.content)
            if matches_twitter != None:
                await message.channel.send(f'<@{message.author.id}>:\n{matches_twitter.groups()[0].replace("twitter", "vxtwitter")}')
                await message.delete()
            
            elif matches_x != None:
                await message.channel.send(f'<@{message.author.id}>:\n{matches_x.groups()[0].replace("x.com", "fixupx.com")}')
                await message.delete()
            
        await self.process_commands(message)

    async def on_member_join(self, usuario : disnake.User):
        self.usuario_servico.registrar(usuario)
        