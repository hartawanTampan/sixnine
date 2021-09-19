from os import path, mkdir
from pyrogram import idle
from sixnine.clients import user, bot
from sixnine import bot_username

if not path.exists("downloads"):
    mkdir("downloads")


async def get_username():
    global bot_username
    x = await bot.get_me()
    bot_username += x.username


user.start()
bot.start()
bot.run(get_username())
print(f"DON'T DELETE THIS, THIS IS FOR DEBUG \nBot username: {bot_username}")
print("=====Bot Running=====\n")

idle()
