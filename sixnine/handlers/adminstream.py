from pyrogram import Client
from pyrogram.types import Message

from sixnine.functions import command, authorized_users_only
from sixnine.clients import player

"""
This method is only can used by admin or sudo users
"""


@Client.on_message(command("pause"))
@authorized_users_only
async def pause_current_playing(_, message: Message):
    await player.pause_stream(message)


@Client.on_message(command("resume"))
@authorized_users_only
async def resume_current_playing(_, message: Message):
    await player.resume_stream(message)


@Client.on_message(command("vol"))
@authorized_users_only
async def change_volume_bot(_, message: Message):
    await player.change_vol(message)
