import os
import asyncio
import discord
from discord.ext import commands
import urllib.request
import shutil
import imageio
import moviepy.editor
import time
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
sthandler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(sthandler)

imageio.plugins.ffmpeg.download()

description = 'automatically compresses animated gif into webm'
token = ('NDE1NTE5NjExNDg5MDkxNTg0.DW3GVA.xeaORHG8j2tIzLlnIv38Hy1YEDA') #stable build account
#token = ('NDE2NTk2NjI1NzM0MTA3MTM4.DXGxXQ.Kxm-9jv_uWLprFg80u73kX3idxw') #unstable build account
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description=description)

@bot.event
async def on_ready():
	print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
	await bot.change_presence(game=discord.Game(name='!gifhelp for info'))

@bot.event
async def on_message(message):
	for attachment in message.attachments:
		if attachment['filename'].split('.')[-1] == 'gif' and message.author != bot.user:
			await bot.delete_message(message)
			try:
				os.remove (message.channel.id + '.gif')
			except FileNotFoundError as e:
				print(str(e) + " on channel " + message.channel.id +". first gif on this channel?")
			await bot.send_typing(message.channel)
			await bot.change_presence(game=discord.Game(name='downloading gif'))
			gifsize = attachment['size']
			link = ('https://cdn.discordapp.com/attachments/' + message.channel.id + '/' + attachment['id'] + '/' + attachment['filename'])
			req = urllib.request.Request(
    			url = link, 
    			data=None, 
    			headers={
        			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    			}
			)
			with urllib.request.urlopen(req) as response, open(message.channel.id + '.gif', 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			await bot.change_presence(game=discord.Game(name='compressing gif'))
			clip = moviepy.editor.VideoFileClip (message.channel.id + '.gif')
			clip.write_videofile('temp.webm')
			webmsize = os.path.getsize('temp.webm')
			await bot.change_presence(game=discord.Game(name='done!'))
			await bot.send_file(message.channel, 'temp.webm')
			await bot.send_message(message.channel, 'original sent by ' + message.author.mention)
			await bot.send_message(message.channel, '```' + str(gifsize/1000) + 'KB compressed to ' + str(webmsize/1000) + 'KB!\n' + str(webmsize/gifsize*100) + '% size of original gif```')
			await asyncio.sleep(5)
			await bot.change_presence(game=discord.Game(name='!gifhelp for info'))
			os.remove ('temp.webm')
	if message.content == "!revert":
		try:
			await bot.send_file(message.channel, message.channel.id + ".gif")
		except FileNotFoundError:
			await bot.send_message(message.channel, "`there is no gif to revert in this channel!`")
		await bot.send_message(message.channel, "`reverted last gif compressed in this channel!`")
	if message.content == "!gifhelp":
		await bot.send_message(message.channel, "```gif compersser 0.7a\nbasic usuage: upload any gif file!\n\navailable commends\n !revert !invite !bench !reportbug_```")
	if message.content.startswith('!reportbug_'):
		if message.content.split('_')[-1] == "":
			await bot.send_message(message.channel, "`commend usuage: !reportbug_(detail)`")
		else:
			owner = bot.get_server('398896214629941248').get_member('343085618387222529')
			await bot.send_message(owner, "bug report from " + message.author.name)
			await bot.send_message(owner, message.content.split('_')[-1])
			await bot.send_message(message.channel, "sent message to developer.\nhe'll respond when he get online.\ncurrent time in developer's contry: https://www.timeanddate.com/worldclock/south-korea/seoul")
	if message.content == "!invite":
		try:
			await bot.send_message(message.author, "invite link: https://discordapp.com/api/oauth2/authorize?client_id=415519611489091584&permissions=43008&scope=bot")
			await bot.send_message(message.channel, "check your DM")
		except discord.errors.Forbidden:
			await bot.send_message(message.channel, "failed to send DM, please allow DM from server member")
	if message.content.startswith("!bench"):
		await bot.send_message(message.channel, "starting benchmark..")
		start_time = time.time()
		try:
			loop = int(message.content.split('!bench')[-1])
		except ValueError as err:
			await bot.send_message(message.channel, str(err) + ". what did you expected when you tell it to run benchmark " + message.content.split('!bench')[-1] + " time?")
		i = 1
		while i <= loop:
			loop_time = time.time()
			clip = moviepy.editor.VideoFileClip("bench.gif")
			clip.write_videofile("bench.webm")
			if i == loop:
				runtime = time.time() - start_time
				await bot.send_message(message.channel, "`benchmark finished! took " + str(time.time() - loop_time) + "s`")
				await bot.send_message(message.channel, "`" + str(runtime) + "s in total`")
				await bot.send_message(message.channel, "`took " + str(runtime / loop) + "s average per run`")
			else:
				await bot.send_message(message.channel, "`benchmark run " + str(i) + "/" + str(loop) + " took " + str(time.time() - loop_time) + " s`")
			os.remove('bench.webm')
			i = i + 1

bot.run(token)