import os
import asyncio
import discord
from discord.ext import commands
import urllib.request
import shutil
import moviepy.editor

description = 'automatically compresses animated gif into webm'
token = ('NDE1NTE5NjExNDg5MDkxNTg0.DW3GVA.xeaORHG8j2tIzLlnIv38Hy1YEDA')
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description=description)

@bot.event
async def on_ready():
	print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
	await bot.change_presence(game=discord.Game(name='waiting for gif'))

@bot.event
async def on_message(message):
	for attachment in message.attachments:
		if attachment['filename'].split('.')[-1] == 'gif':
			bot.delete_message(message)
			await bot.send_typing(message.channel)
			await bot.change_presence(game=discord.Game(name='downloading gif'))
			gifsize = attachment['size']
			uasnoof = "{'User-Agent' : 'Chrome/23.0.1271.95'}"
			link = ('https://cdn.discordapp.com/attachments/' + message.channel.id + '/' + attachment['id'] + '/' + attachment['filename'])
			req = urllib.request.Request(
    			url = link, 
    			data=None, 
    			headers={
        			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    			}
			)
			with urllib.request.urlopen(req) as response, open('temp.gif', 'wb') as out_file:
				shutil.copyfileobj(response, out_file)
			await bot.change_presence(game=discord.Game(name='compressing gif'))
			clip = moviepy.editor.VideoFileClip ('temp.gif')
			clip.write_videofile('temp.webm')
			webmsize = os.path.getsize('temp.webm')
			os.remove ('temp.gif')
			await bot.change_presence(game=discord.Game(name='done!'))
			await bot.send_file(message.channel, 'temp.webm')
			await bot.send_message(message.channel, 'original sent by ' + message.author.name)
			await bot.send_message(message.channel, '```' + str(gifsize/1000) + 'KB compressed to ' + str(webmsize/1000) + 'KB!```')
			await bot.send_message(message.channel, '```' + str(webmsize/gifsize*100)) + '% size of original gif```'
			await asyncio.sleep(5)
			await bot.change_presence(game=discord.Game(name='waiting for gif'))
			os.remove ('temp.webm')

bot.run(token)