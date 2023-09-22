import disnake
from disnake.ext import commands, tasks
import re
from datetime import datetime, timezone
from random import randint
from comandos.Perfil import registrar
from comandos.Xp import obter_level
from save_and_load import *
import codecs


intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

bot.load_extensions("comandos")
bot.xp_adicionado = []

bot.configs = carregar("configs")

@tasks.loop(seconds=59)
async def loop_1m():
    bot.xp_adicionado = []
    
    horario = datetime.now(timezone.utc)
    minuto = horario.minute
    hora = horario.hour - 3
    if hora < 0:
        hora = 24 + hora
    
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
            await bot.channel_geral.send("Bom dia!!!\n" + imagens_link[aleatorio])
        
        elif hora == 13:
            imagens_link = [
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/mensagens-de-boa-tarde-ka0z3-fxl.jpg?w=1200&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/8edfee13bbfe582be562c0caec2559d4-cute-kittens-funny-dogs.jpg?w=540&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/69ac6533cbd5e546bea791a1aec4486b-nadir-pasta.jpg?w=511&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/179.jpg?w=632&ssl=1",
                "https://i0.wp.com/emotioncard.com.br/wp-content/uploads/2017/07/2016-Abril-28-Boa-tarde-IMG-2.jpg?w=720&ssl=1"
            ]
            await bot.channel_geral.send("Boa tarde!\n" + imagens_link[aleatorio])

        elif hora == 19:
            imagens_link = [
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2022/09/imagem-de-boa-noite.png?resize=768%2C798&ssl=1",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Boa-noite-a-todos.jpg?w=360&ssl=1",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2020/12/Que-Deus-abencoe-a-sua-noite-e-te-der-lindos-sonhos.jpg?w=480&ssl=1",
                "https://i.pinimg.com/564x/12/d1/cc/12d1cc49b307e23f6cab2d9bd07bd670.jpg",
                "https://i0.wp.com/amaluz.com.br/wp-content/uploads/2021/12/Boa-noite-Nada-e-dificil-quando-temos-fe-em-Deus-e-na-vida.jpg?w=700&ssl=1"
            ]
            await bot.channel_geral.send("Boa noite!!!\n" + imagens_link[aleatorio])

        elif hora == 8:
            dia = datetime.now(timezone.utc)
            mes = '%02d' % dia.month
            dia = '%02d' % dia.day
            membros = carregar()
            for key, niver in membros.items():
                if niver["aniversario"] == dia + "/" + mes:
                    await bot.channel_geral.send("<@" + key + "> FELIZ ANIVERSÁRIO!!!\nhttps://media.discordapp.net/attachments/842921629054271518/1050245621954641950/happy_birthday.mp4")
                    break

@bot.event
async def on_slash_command_error(inter : disnake.ApplicationCommandInteraction, 
                                 exception : commands.CommandError):
    try:
        await inter.response.defer()
    except:
        pass
    
    await bot.owner.send(f"## Ocorreu um erro: " +
                            f"\n- Servidor: **{inter.guild.name}**" +
                            f"\n- Canal: **{inter.channel.name}** às **{datetime.now().strftime('%H:%M:%S, %Y/%m/%d')}**" + 
                            f"\n- Usuário: **{inter.user.name}**" + 
                            f"\n- Comando: **{inter.application_command.name}**" +
                            f"\n- Exceção: \n```{exception}```")
    
    await inter.edit_original_message("Ocorreu um erro :(")

@bot.event
async def on_ready():
    loop_1m.start()
    
    membros = carregar()
    deletar = []
    for id, conteudo in membros.items():
        usuario = bot.get_user(int(id))
        if usuario == None:
            deletar.append(id)
    for id in deletar:
        del membros[id]
    salvar(membros)    
    
    bot.channel_geral = bot.get_channel(bot.configs["canais"]["geral"])

@bot.event
async def on_message(message : disnake.message.Message):
    if not message.author.bot:
        if bot.configs["xp"]["ativo"] and message.author.id not in bot.xp_adicionado and not message.author.bot:
            valor_canais_xp = carregar("valor_canais_xp")
            membros = carregar()
            
            valor_xp = 0
            for valor_canal, lista_canais in valor_canais_xp.items():
                if valor_xp < float(valor_canal):
                    if message.channel.id in lista_canais:
                        valor_xp = float(valor_canal)
            valor_xp = 1 if valor_xp == 0 else valor_xp
            xp = membros[str(message.author.id)]["xp"]
        
            lvl_anterior = obter_level(xp)[0]
            xp += randint(int(15 * valor_xp), int(25 * valor_xp)) * bot.configs["xp"]["multiplicador"]
            lvl_posterior = obter_level(xp)[0]
            
            membros[str(message.author.id)]["xp"] = xp
            canal_lvl_up = bot.get_channel(bot.configs["canais"]["xp"])
            if lvl_anterior != lvl_posterior:
                await canal_lvl_up.send(f"<@{message.author.id}> acaba de upar para o level {lvl_posterior}!")
            
            salvar(membros)
            
            bot.xp_adicionado.append(message.author.id)
        
        if bot.user.mentioned_in(message):
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
        
        reacoes = bot.configs["reacoes"]
        
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
        
    await bot.process_commands(message)

@bot.event
async def on_member_join(usuario : disnake.User):
    registrar(usuario)

@bot.before_slash_command_invoke
async def before_slash_command_invoke(inter : disnake.ApplicationCommandInteraction):
    registrar(inter.user)

key = carregar("keys")["key"]
bot.run(key)
