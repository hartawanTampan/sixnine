from pyrogram import Client
from dB import add_sudo, del_sudo, get_sudos
from sixnine.functions import command, authorized_users_only
from pyrogram.types import Message


@Client.on_message(command("addsudo"))
@authorized_users_only
async def add_sudo_to_chat(_, message: Message):
    replied = message.reply_to_message
    chat_id = message.chat.id
    if not replied:
        sudo_id = int(message.command[1])
        if sudo_id:
            try:
                add_sudo(chat_id, sudo_id)
                await message.reply("success add sudo")
            except Exception as Ex:
                await message.reply(
                    f"{type(Ex).__name__}: {str(Ex.with_traceback(Ex.__traceback__))}"
                )
            return
        elif message.command[1].startswith("@"):
            try:
                username = message.command[1].split("@")[1]
                user_id = (await message.chat.get_member(username)).user.id
                add_sudo(chat_id, user_id)
                await message.reply("success add to sudo users")
            except Exception as e:
                await message.reply(
                    f"{type(e).__name__}: {e.with_traceback(e.__traceback__)}"
                )
                return
        return
    sudo_id = replied.from_user.id
    try:
        add_sudo(chat_id, sudo_id)
        await message.reply("success add sudo")
    except Exception as Ex:
        await message.reply(
            f"{type(Ex).__name__}: {str(Ex.with_traceback(Ex.__traceback__))}"
        )
    return


@Client.on_message(command("delsudo"))
@authorized_users_only
async def del_sudo_from_chat(_, message: Message):
    replied = message.reply_to_message
    chat_id = message.chat.id
    if not replied:
        sudo_id = int(message.command[1])
        try:
            del_sudo(chat_id, sudo_id)
            await message.reply("delete sudo success")
        except Exception as e:
            await message.reply(
                f"{type(e).__name__}: {str(e.with_traceback(e.__traceback__))}"
            )
        return
    sudo_id = replied.from_user.id
    try:
        del_sudo(chat_id, sudo_id)
        await message.reply("delete sudo successfully")
    except Exception as e:
        await message.reply(
            f"{type(e).__name__}: {str(e.with_traceback(e.__traceback__))}"
        )
    return


@Client.on_message(command("getsudos"))
async def get_all_sudo_in_chat(client: Client, message: Message):
    chat_id = message.chat.id
    y = ""
    for x in get_sudos(chat_id):
        n = await client.get_users(x)
        y += f"{n.first_name} {n.last_name if n.last_name else ''} ({x})\n"
    await message.reply(f"{y}")
