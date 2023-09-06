import disnake
from disnake.ext import commands, tasks
import re
from datetime import datetime, timezone
from random import randint
from save_and_load import *


intents = disnake.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

client.load_extension("comandos.anime")
client.load_extension("comandos.jogo")
client.load_extension("comandos.perfil")
client.load_extension("comandos.twitch")
client.load_extension("comandos.comandos")


@tasks.loop(seconds=59)
async def send_message():
    horario = datetime.now(timezone.utc)
    minuto = horario.minute
    hora = horario.hour - 3
    if hora < 0:
        hora = 24 + hora
    # uniao sinistra
    if minuto == 00:
        aleatorio = randint(0,4)
        if hora == 7:
            imagens_link = [
                "https://cdn.discordapp.com/attachments/1054167826937688067/1055609966997811251/bomdia_1.webp",
                "https://cdn.discordapp.com/attachments/1054167826937688067/1055609967513698434/bomdia_2.jpg",
                "https://cdn.discordapp.com/attachments/1054167826937688067/1055609967811506245/bomdia_3.webp",
                "https://cdn.discordapp.com/attachments/1054167826937688067/1055609968230932620/bomdia_4.jpg",
                "https://cdn.discordapp.com/attachments/1054167826937688067/1055609966804860948/bomdia_5.jpg"
            ]
            await client.channel_geral.send("Bom dia!!!\n" + imagens_link[aleatorio])
        
        elif hora == 13:
            imagens_link = [
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/mensagens-de-boa-tarde-ka0z3-fxl.jpg?w=1200&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/8edfee13bbfe582be562c0caec2559d4-cute-kittens-funny-dogs.jpg?w=540&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/69ac6533cbd5e546bea791a1aec4486b-nadir-pasta.jpg?w=511&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/179.jpg?w=632&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/2016-Abril-28-Boa-tarde-IMG-2.jpg?w=720&ssl=1"
            ]
            await client.channel_geral.send("Boa tarde!\n" + imagens_link[aleatorio])

        elif hora == 19:
            imagens_link = [
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2022/09/imagem-de-boa-noite.png?resize=768%2C798&ssl=1",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Boa-noite-a-todos.jpg?w=360&ssl=1",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Que-Deus-abencoe-a-sua-noite-e-te-der-lindos-sonhos.jpg?w=480&ssl=1",
                "https://i.pinimg.com/564x/12/d1/cc/12d1cc49b307e23f6cab2d9bd07bd670.jpg",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2021/12/Boa-noite-Nada-e-dificil-quando-temos-fe-em-Deus-e-na-vida.jpg?w=700&ssl=1"
            ]
            await client.channel_geral.send("Boa noite!!!\n" + imagens_link[aleatorio])

        elif hora == 8:
            membros = carregar()
            dia = datetime.now(timezone.utc)
            mes = '%02d' % dia.month
            dia = '%02d' % dia.day
            for key, niver in membros.items():
                if niver["aniversario"] == dia + "/" + mes:
                    await client.channel_geral.send("<@" + key + "> FELIZ ANIVERSÁRIO!!!\nhttps://media.discordapp.net/attachments/842921629054271518/1050245621954641950/happy_birthday.mp4")
                    break

client.on_slash_command_error
@client.event
async def on_slash_command_error(inter : disnake.ApplicationCommandInteraction, 
                                 exception : commands.CommandError):
    try:
        await inter.response.defer()
    except:
        pass
    
    await client.owner.send(f"## Ocorreu um erro: " +
                            f"\n- Servidor: **{inter.guild.name}**" +
                            f"\n- Canal: **{inter.channel.name}** às **{datetime.now().strftime('%H:%M:%S, %Y/%m/%d')}**" + 
                            f"\n- Usuário: **{inter.user.name}**" + 
                            f"\n- Comando: **{inter.application_command.name}**" +
                            f"\n- Exceção: \n```{exception}```")
    
    await inter.edit_original_message("Ocorreu um erro :(")

@client.event
async def on_ready():
    send_message.start()
    client.channel_geral = client.get_channel(842921629054271518)
    client.channel_teste = client.get_channel(1054167826937688067)

@client.event
async def on_message(inter : commands.Context):
    if client.user.mentioned_in(inter):
        data = datetime.now(timezone.utc)
        hora = data.hour - 3
        autor = inter.author.id

        if 7 <= hora < 13 and "bom dia" in inter.content.lower() and autor != client.user.id:
            await inter.channel.send("<@" + str(autor) + "> Bom dia !!!")
        elif 13 <= hora < 19 and "boa tarde" in inter.content.lower() and autor != client.user.id:
            await inter.channel.send("<@" + str(autor) + "> Boa tarde !!!")
        elif "boa noite" in inter.content.lower() and autor != client.user.id:
            await inter.channel.send("<@" + str(autor) + "> Boa noite !!!")

        if "feliz ano novo" in inter.content.lower():
            await inter.channel.send("<@" + str(autor) + "> Feliz ano novo para você !!! Espero que você tenha um ótimo 2012!!!")
    
    reacoes = {
        "mey": '\U00002764',
        "ruan": '\U0001F308',
        "olavo": '\U0001F480',
        "sasa": ':sasadaph:1056344897919123506',
        "sasa": ':sasadaph:1056344897919123506',
        "vitin": '\U0001F48B',
        "727": ':wysi:997606675576016956',
        "bananinho": '\U0001F34C'
    }
    
    for chave, reacao in reacoes.items():
        if chave in inter.content.lower():
            await inter.add_reaction(reacao)
    
    # vxtwitter
    matches = re.match(r"(https://twitter.com/.*?/status/\w*)", inter.content)
    if matches != None and inter.author.id != client.user.id:
        await inter.reply(matches.groups()[0].replace("twitter", "vxtwitter"))
        
    await client.process_commands(inter)

@client.event
async def on_member_join(member : disnake.User):
    membros = carregar()
    if str(member.id) not in membros:
        membros[str(member.id)] = {
                "nick": member.name,
                "nome": "Não informado",
                "aniversario": "Não informado",
                "estado": "Não informado",
                "twitter": "Não informado",
                "twitch": "Não informado",
                "lista_animes": "Não informado",
                "steam": "Não informado",
                "instagram": "Não informado",
                "osu": "Não informado",
                "genshin_uid": "Não informado",
                "bruno_points": 0
            }
        salvar(membros)


key = carregar("keys")["key"]
client.run(key)
