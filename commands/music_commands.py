import os

import discord
from discord.ext import commands
import youtube_dl

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
        song_valid = os.path.isfile("song.m4a")

        try:
            if song_valid:
                os.remove("song.m4a")
        except PermissionError:
            await ctx.send("song is playing")
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
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".m4a"):
                os.rename(file, "song.m4a")
        voice.play(discord.FFmpegPCMAudio("song.m4a"))

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