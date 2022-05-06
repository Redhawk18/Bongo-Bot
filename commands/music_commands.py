#TODO make bot switch vc's
#TODO handle error when user isnt in vc
#TODO look into why the video some times has noise

import asyncio
import os
from queue import Queue

import discord
from discord.ext import commands
from discord.ext.commands.errors import ClientException
from yt_dlp import YoutubeDL

class Music_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.q = Queue(0)
        self._is_playing_song = False
        self._ydl_opts = { 
                'format': 'bestaudio/best',
                'noplaylist': True,

                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus', },
                    {'key': 'SponsorBlock'},
                    {'key': 'ModifyChapters', 'remove_sponsor_segments': ['sponsor', 'interaction', 'music_offtopic']}
                ],
            }
        

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")


    @commands.command()
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_connected():
            await voice.stop()
            await voice.disconnect()
            await ctx.send("**Disconnected** :guitar:")

        else:
            await ctx.send("Already disconnected")


    async def _play_next_song(self, error=None):
        if os.path.isfile('song.opus'):
            os.remove('song.opus')

        if self.q.empty():
            self._is_playing_song = False
            print('No more songs in queue')
            return

        
        next_url, ctx = self.q.get()
        print(f'Playing next song: {next_url}')

        self._is_playing_song = True

        voice_channel = ctx.author.voice.channel

        try: #connect to channel
            await voice_channel.connect()
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            await ctx.send(f'**Connected** :drum: to `{str(voice_channel)}`')

        except ClientException: #already connected
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        with YoutubeDL(self._ydl_opts) as ydl: #download audio
            ydl.download([next_url])
            info_dict = ydl.extract_info(next_url, False)

        for file in os.listdir(os.getcwd()):
            if file.endswith('.opus'):
                os.rename(file, 'song.opus')

        voice.play(discord.FFmpegPCMAudio('song.opus'), after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next_song(e), self.client.loop))
        await ctx.send(f"**Playing** :notes: `{info_dict.get('title', None)}` - Now!")
        

    @commands.command()
    async def play(self, ctx, url : str): 
        self.q.put((url, ctx))
        if not self._is_playing_song:
            await self._play_next_song(None)
        else:
            await ctx.send(f"**Added** :musical_note: `{url}` to queue")


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
    async def forceskip(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        
        if voice.is_playing():
            voice.stop()
            await ctx.send("**Skipped** :fast_forward:")

        else:
            await ctx.send("Nothing is playing")


def setup(client):
    client.add_cog(Music_Commands(client))