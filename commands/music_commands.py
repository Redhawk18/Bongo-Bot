import os

import discord
from discord.ext import commands
from discord.ext.commands.errors import ClientException
from yt_dlp import YoutubeDL

class Music_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")

    @commands.command()
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_connected():
            await voice.disconnect()
            await ctx.send("**Disconnected** :guitar:")
        else:
            await ctx.send("Already disconnected")

    #commands
    @commands.command()
    async def play(self, ctx, url : str): 
        #TODO make bot switch vc's
        #TODO handle error when user isnt in vc
        #TODO look into why the video some times has noise
        #TODO add queue
        song_valid = os.path.isfile("song.opus")
        try:
            if song_valid: #no song is playing, removing old song file
                os.remove("song.opus")

        except PermissionError: #if a current song is playing
            await ctx.send("song is playing, i havent put a queue system in yet") 
            return

        #find current vc
        voiceChannel = ctx.author.voice.channel
        try: #connect to channel
            await voiceChannel.connect()
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            await ctx.send("**Connected** :drum: to `" + str(voiceChannel) +"`")

        except ClientException: #already connected
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        

        ydl_opts = { 
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '256',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, False)
        for file in os.listdir("./"):
            if file.endswith(".opus"):
                os.rename(file, "song.opus")
        voice.play(discord.FFmpegPCMAudio("song.opus"))
        output = "**Playing** :notes: `" + info_dict.get('title', None) + "` - Now!"
        await ctx.send(output)

    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
            await ctx.send("**Paused** :pause_button:")

        else:
            await ctx.send("Nothing is playing")
            
    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
            await ctx.send("**Resumed** :arrow_forward:")

        else:
            await ctx.send("Nothing is paused")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()


def setup(client):
    client.add_cog(Music_Commands(client))