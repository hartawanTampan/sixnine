import asyncio
import random
import sys

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.types import Message, CallbackQuery
from pytgcalls import GroupCallFactory
from pytgcalls.exceptions import GroupCallNotFoundError

from dB.getlang import get_message
from sixnine.configs import config
from sixnine.functions import get_youtube_stream

user = Client(
	config.SESSION,
	config.API_ID,
	config.API_HASH
)

bot = Client(
	":memory:",
	config.API_ID,
	config.API_HASH,
	bot_token=config.BOT_TOKEN,
	plugins=dict(root="sixnine.handlers")
)


class Player:
	def __init__(self):
		self.call = GroupCallFactory(user)
		self._client = {}
		self.playlist: dict[int, list[dict[str, str]]] = {}

	async def _dummy_stream(self, query: str, message: Message, downloaded_video, y):
		playlist = self.playlist
		call = self.call.get_group_call()
		chat_id = message.chat.id
		playlist[chat_id] = [{"query": query}]
		await call.join(chat_id)
		await y.edit(get_message(chat_id, "stream").format(query))
		await call.start_video(downloaded_video, True, False, True)
		self._client[chat_id] = call

		@self._client[chat_id].on_playout_ended
		async def playout_ended(gc, source, media):
			if len(self.playlist[chat_id]) > 1:
				self.playlist[chat_id].pop(0)
				query = self.playlist[chat_id][0]['query']
				downloaded_video = await get_youtube_stream(query)
				await self._client[chat_id].start_video(downloaded_video, True, False, True)
				await message.reply(f"Skipped track, and playing {query}")
				return
			await self._client[chat_id].leave_current_group_call()

	async def _dummy_start_stream(self, query, message):
		chat_id = message.chat.id
		playlist = self.playlist
		if len(playlist) >= 1:
			try:
				playlist[chat_id].extend([{'query': query}])
				y = await message.reply("Queued")
				await asyncio.sleep(3)
				await y.delete()
				return
			except KeyError:
				await message.reply("restart the bot")
				return
		y = await message.reply(get_message(chat_id, "process"))
		downloaded_video = await get_youtube_stream(query)
		try:
			await self._dummy_stream(query, message, downloaded_video, y)
		except FloodWait as Fwx:
			await message.reply(f"Getting floodwait {Fwx.x} second, bot is sleeping")
			await asyncio.sleep(Fwx.x)
			await self._dummy_stream(query, message, downloaded_video, y)
		except GroupCallNotFoundError:
			try:
				await user.send(CreateGroupCall(
					peer=await user.resolve_peer(chat_id),
					random_id=random.randint(10000, 999999999)
				))
				await self._dummy_stream(query, message, downloaded_video, y)
			except Exception as ex:
				print(ex)
				sys.exit(1)
		except Exception as ex:
			print(ex)
			sys.exit(1)

	async def start_stream(self, query: str, message: Message):
		await self._dummy_start_stream(query, message)

	async def start_stream_via_callback(self, query: str, callback: CallbackQuery):
		message = callback.message
		await self._dummy_start_stream(query, message)

	async def end_stream(self, message: Message):
		chat_id = message.chat.id
		playlist = self.playlist
		if self._client[chat_id].is_connected:
			await self._client[chat_id].stop()
			playlist[chat_id].clear()
			await message.reply("ended")
		else:
			await message.reply("Not in call")

	async def change_vol(self, message: Message):
		vol = int("".join(message.command[1]))
		chat_id = message.chat.id
		try:
			if self._client[chat_id].is_connected:
				try:
					await self._client[chat_id].edit_group_call(vol, False, False, False)
					await message.reply(f"volume changed to {vol}")
				except Exception as eX:
					await message.reply(str(eX.with_traceback(eX.__traceback__)))
			else:
				await message.reply("not playing")
		except KeyError:
			await message.reply("stream first")

	# Pause Resume dll
	async def pause_stream(self, message: Message):
		chat_id = message.chat.id
		if self._client[chat_id].is_paused:
			await message.reply("already paused")
			return
		await self._client[chat_id].set_pause(True)
		await message.reply("paused")

	async def resume_stream(self, message: Message):
		chat_id = message.chat.id
		if not self._client[chat_id].is_paused:
			await message.reply("already playing")
			return
		await self._client[chat_id].set_pause(False)
		await message.reply("resumed")

	async def change_stream(self, message: Message):
		chat_id = message.chat.id
		playlist = self.playlist
		if len(playlist[chat_id]) > 1:
			playlist[chat_id].pop(0)
			query = playlist[chat_id][0]['query']
			downloaded_video = await get_youtube_stream(query)
			await self._client[chat_id].start_video(downloaded_video, True, False, True)
			await message.reply(f"Skipped track, and playing {query}")
			return
		await message.reply("No playlist")
	# End of pause resume dll

	async def send_playlist(self, message: Message):
		chat_id = message.chat.id
		playlist = self.playlist[chat_id]
		if len(playlist) >= 1:
			await message.reply(f"This is playlist\n{playlist}")
			return
		await message.reply("No playlist")


player = Player()
