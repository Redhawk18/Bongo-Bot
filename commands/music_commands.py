import asyncio
from collections import deque
from math import floor
import os
import urllib.parse, urllib.request, re

import discord
from discord.ext import commands
from discord.ext.commands.errors import ClientException, CommandInvokeError
from yt_dlp import YoutubeDL, DownloadError

class Music_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.q = deque()
        self._is_playing_song = False
        self.loop_enabled = False
        self.how_many_want_to_skip = 0
        #self.music_channel = None
        self.music_channel = 'music-spam' #makes testing easier 
        self._ydl_opts = { 
                'format': 'bestaudio/best',
                'extract_flat': True, 

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


    @commands.command(aliases=['fuckoff', 'd', 'dc'])
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_connected():
            self.q.clear() #wipe all future songs
            voice.stop()
            await voice.disconnect()
            await ctx.send("**Disconnected** :guitar:")

        else:
            await ctx.send("Already disconnected")


    @commands.command()
    async def musicchannel(self, ctx):
        #set authors text channel
        self.music_channel = ctx.channel.name
        await ctx.send(f'{str(self.music_channel)} will be the only text channel the bot will take and output music commands from')


    async def _is_music_channel(self, ctx):
        """compares authors text channel to the set music channel"""
        if ctx.channel.name == self.music_channel:
            return True

        await ctx.send("Wrong channel for music commands")
        return False


    async def _in_voice_channel(self, ctx):
        """Users have to be in a voice channel"""
        try: #checks if the author is in a voice channel
            ctx.author.voice.channel

        except AttributeError: # user isnt in any voice channel
            await ctx.send("You are not in a voice channel")
            return False

        return True


    async def _play_next_song(self, error=None, ctx=None):
        """figures out what voice channel the user is in, and joins. Then it downloads and encodes and plays from the queue"""
        if os.path.isfile('song.opus'):
            os.remove('song.opus')

        if len(self.q) == 0: #base case
            self._is_playing_song = False
            print('No more songs in queue')
            await self.disconnect(ctx)
            return


        next_url, ctx = self.q.pop()
        if self.loop_enabled:
            self.q.append((next_url, ctx))
    
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
            info_dict = ydl.extract_info(next_url, False)

            #check if the link is a playlist
            if info_dict.get('_type', None) != None:
                #call _add_videos_from_playlist function to deal with it
                await self._add_videos_from_playlist(ctx, next_url)
                await ctx.send(f'**Added Playlist** :musical_note: `{next_url}` to queue')
                next_url, ctx = self.q.pop() #since we added a butch of new urls and the current next_url is a playlist
                info_dict = ydl.extract_info(next_url, False) #new video new metadata

            ydl.download([next_url])

        for file in os.listdir(os.getcwd()):
            if file.endswith('.opus'):
                os.rename(file, 'song.opus')

        voice.play(discord.FFmpegOpusAudio('song.opus'), after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next_song(e, ctx), self.client.loop))
        await ctx.send(f"**Playing** :notes: `{info_dict.get('title', None)}` by `{info_dict.get('channel', None)}` - Now!")
        

    async def _add_videos_from_playlist(self, ctx, playlist_url):
        #extract_flat false so we can take videos out one by one
        with YoutubeDL({'extract_flat': False}) as ydl:
            #get the info_dict with all playlist videos
            playlist_info_dict = ydl.extract_info(playlist_url, False)
            video_url = ""

            for index in range(len(playlist_info_dict.get('entries', None))):
                 video_url = playlist_info_dict.get('entries')[index].get('webpage_url')
                 #add that to queue  
                 self.q.appendleft((video_url, ctx))


    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query : str, is_playnext=None): 
        if not await self._in_voice_channel(ctx) or not await self._is_music_channel(ctx):
            return
        
        query_string = urllib.parse.urlencode({
            'search_query': query
        })
        htm_content = urllib.request.urlopen(
            'https://www.youtube.com/results?' + query_string
        )
        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        url = 'https://www.youtube.com/watch?v=' + search_results[0]

        #start play proccess with url
        if not is_playnext:
            self.q.appendleft((url, ctx))
        elif is_playnext:
            self.q.append((url, ctx))

        if not self._is_playing_song:
            await self._play_next_song(None)
        else:
            if not is_playnext:
                await ctx.send(f"**Added** :musical_note: `{url}` to queue")
            elif is_playnext:
                await ctx.send(f"**Added** :musical_note: `{url}` to the top of the queue")
            

    @commands.command(aliases=['playtop'])
    async def playnext(self, ctx, *, query : str): 
        await self.play(ctx, query=query, is_playnext=True)

    @commands.command()
    async def playurl(self, ctx, url : str):
        if not await self._in_voice_channel(ctx) or not await self._is_music_channel(ctx):
            return

        #this function HAS TO have a valid url
        if 'https://www.youtube.com/watch?v=' in url or 'https://youtu.be/' in url:
            #link might be valid
            try:
                with YoutubeDL(self._ydl_opts) as ydl: #download audio
                    ydl.extract_info(url, False) #TODO sending to api is really slow replace with better trycatch
            except DownloadError: #if video doesnt exist
                await ctx.send("Invalid url")
                return

            self.q.appendleft((url, ctx))

            if not self._is_playing_song:
                await self._play_next_song(None)
            else:
                await ctx.send(f"**Added** :musical_note: `{url}` to queue")
        else:
            await ctx.send("Invalid url")


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

        if voice.is_paused():
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
            self.how_many_want_to_skip = 0 #reset counter
            voice.stop()
            await ctx.send("**Skipped** :fast_forward:")

        else:
            await ctx.send("Nothing is playing")


    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        if not await self._in_voice_channel(ctx):
            return
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            #increase the how_many_want_to_skip
            self.how_many_want_to_skip += 1

            #check if its passed threshold
            voice_channel = ctx.author.voice.channel
            threshold = floor((len(voice_channel.members)-1)/2) #-1 for the bot

            if self.how_many_want_to_skip >= threshold: #enough people
                await self.forceskip(ctx)
            
            else: #not enough people
                await ctx.send(f'**Skipping? ({self.how_many_want_to_skip}/{threshold} people) or use `forceskip`**')

        else:
            await ctx.send("Nothing is playing")
            return


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
            if seconds < 10: #time like 2:0 -> 2:00
                seconds = "0" + str(seconds)

            output += (f"{index +1}. `{info_dict.get('title', None)}` - `{minutes}:{seconds}`\n")
            index += 1

        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def queueclear(self, ctx):
        self.q.clear()
        await ctx.send("**Cleared queue** :books:")


    @commands.command()
    async def queueremove(self, ctx, queue_position : int):
        if queue_position > len(self.q) or queue_position < 0:
            await ctx.send("Input invalid")
            return

        #because of how the remove function works we have to make a copy
        tempq = self.q.copy()

        for index in range(queue_position -1): #so we dont have to save what's popped
            tempq.pop()

        #we should have the url of the track we want to remove
        self.q.remove(tempq.pop())
        await ctx.send("**Removed from queue** :books:")


    @commands.command()
    async def loop(self, ctx):
        if self.loop_enabled: #disable loop
            self.loop_enabled = False
            await ctx.send("**Loop Disabled** :repeat:")

        else: #enable loop
            self.loop_enabled = True
            await ctx.send("**Loop Enabled** :repeat:")



def setup(client):
    client.add_cog(Music_Commands(client))