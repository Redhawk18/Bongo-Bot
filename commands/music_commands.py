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
    async def connect(self, ctx):
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="General") #TODO fix General only
        #connect to channel
        try:
            await voiceChannel.connect()
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        except ClientException: 
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        await ctx.send("**Connected** :drum:")
        return voice
        

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
        song_valid = os.path.isfile("song.mp3")
        try:
            if song_valid: #no song is playing, removing old song file
                os.remove("song.mp3")

        except PermissionError: #if a current song is playing
            await ctx.send("song is playing, i havent put a queue system in yet") #TODO add queue
            return

        voice = ctx.invoke.connect(self, ctx)

        ydl_opts = { #TODO look into why the video some times has noise
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, False)
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        voice.play(discord.FFmpegPCMAudio("song.mp3"))
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