#TODO make bot switch vc's
#TODO look into why the video some times has noise

import asyncio
from collections import deque
import os
import urllib.parse, urllib.request, re

import discord
from discord.ext import commands
from discord.ext.commands.errors import ClientException, CommandInvokeError
from yt_dlp import YoutubeDL

class Music_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.q = deque()
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
        

    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")


    @commands.command(aliases=['fuckoff', 'd'])
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_connected():
            self.q.clear() #wipe all future songs
            voice.stop()
            await voice.disconnect()
            await ctx.send("**Disconnected** :guitar:")

        else:
            await ctx.send("Already disconnected")


    async def _in_voice_channel(self, ctx):
        """Users have to be in a voice channel"""
        try: #checks if the author is in a voice channel
            ctx.author.voice.channel

        except AttributeError: # user isnt in any voice channel
            await ctx.send("You are not in a voice channel")
            return False

        return True


    async def _play_next_song(self, error=None):
        if os.path.isfile('song.opus'):
            os.remove('song.opus')

        if len(self.q) == 0: #base case
            self._is_playing_song = False
            print('No more songs in queue')
            return


        next_url, ctx = self.q.pop()
    
        try: #connect to channel
            voice_channel = ctx.author.voice.channel # error is handled eariler
            await voice_channel.connect()
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            await ctx.send(f'**Connected** :drum: to `{str(voice_channel)}`')

        except ClientException: #already connected
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        self._is_playing_song = True
        print(f'Playing next song: {next_url}')

        with YoutubeDL(self._ydl_opts) as ydl: #download audio
            ydl.download([next_url])
            info_dict = ydl.extract_info(next_url, False)

        for file in os.listdir(os.getcwd()):
            if file.endswith('.opus'):
                os.rename(file, 'song.opus')

        voice.play(discord.FFmpegOpusAudio('song.opus'), after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next_song(e), self.client.loop))
        await ctx.send(f"**Playing** :notes: `{info_dict.get('title', None)}` by `{info_dict.get('channel', None)}` - Now!")
        

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, search : str): 
        if not await self._in_voice_channel(ctx):
            return

        #search youtube for url
        query_string = urllib.parse.urlencode({
            'search_query': search
        })
        htm_content = urllib.request.urlopen(
            'https://www.youtube.com/results?' + query_string
        )
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = 'https://www.youtube.com/watch?v=' + search_results[0]

        #start play proccess with url
        self.q.appendleft((url, ctx))
        if not self._is_playing_song:
            await self._play_next_song(None)
        else:
            await ctx.send(f"**Added** :musical_note: `{url}` to queue")


    @commands.command()
    async def pause(self, ctx):
        if not await self._in_voice_channel(ctx):
            return
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
            await ctx.send("**Paused** :pause_button:")

        else:
            await ctx.send("Nothing is playing")


    @commands.command()
    async def resume(self, ctx):
        if not await self._in_voice_channel(ctx):
            return
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
            await ctx.send("**Resumed** :arrow_forward:")

        else:
            await ctx.send("Nothing is paused")


    @commands.command(aliases=['fs', 'fskip'])
    async def forceskip(self, ctx):
        if not await self._in_voice_channel(ctx):
            return
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        
        if voice.is_playing():
            voice.stop()
            await ctx.send("**Skipped** :fast_forward:")

        else:
            await ctx.send("Nothing is playing")


    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        tempq = self.q.copy()

        #incase the queue was empty from the start
        if len(tempq) == 0:
            await ctx.send("The queue is empty")
            return

        #store every element in a string
        index = 0
        output = ""
        while tempq:
            #get the url of the video
            current_url, unused_ctx = tempq.pop()
            with YoutubeDL(self._ydl_opts) as ydl: #download metadata
                info_dict = await asyncio.to_thread(ydl.extract_info, current_url, False)
                
            minutes, seconds = divmod(info_dict.get('duration', None), 60)
            output += (f"{index +1}. `{info_dict.get('title', None)}` - `{minutes}:{seconds}`\n")
            index += 1

        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Music_Commands(client))