import os

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

class Music_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")

    #commands
    @commands.command()
    async def play(self, ctx, url : str):
        song_valid = os.path.isfile("song.opus")

        try:
            if song_valid:
                os.remove("song.opus")
        except PermissionError:
            await ctx.send("song is playing, i havent put a queue system in yet")
            return

        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="General") #TODO fix this

        #connect to channel
        await voiceChannel.connect()
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        #if not voice.is_connected():
        

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredquality': '192',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".opus"):
                os.rename(file, "song.opus")
        voice.play(discord.FFmpegPCMAudio("song.opus"))

    @commands.command()
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("Already disconnected")

    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Nothing is playing")
            
    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
        else:
            await ctx.send("Nothing is paused")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()


def setup(client):
    client.add_cog(Music_Commands(client))