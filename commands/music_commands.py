import asyncio
from collections import deque
from math import floor
import os
import urllib.parse, urllib.request, re

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.errors import ClientException, CommandInvokeError
import yt_dlp
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


    @app_commands.command(name='disconnect', description='disconnect from voice chat')
    async def disconnect(self, interaction: discord.Interaction):
        voice = interaction.guild.voice_client

        if voice.is_connected():
            self.q.clear() #wipe all future songs
            self._is_playing_song = False
            voice.stop()
            await voice.disconnect()
            await interaction.response.send_message("**Disconnected** :guitar:")

        else:
            await interaction.response.send_message("Already disconnected")


    @app_commands.command()
    async def musicchannel(self, interaction: discord.Interaction): #TODO make a json or something to store settings
        #set authors text channel
        self.music_channel = interaction.channel.name
        await interaction.response.send_message(f'{str(self.music_channel)} will be the only text channel the bot will take and output music commands from')


    async def _is_music_channel(self, interaction: discord.Interaction):
        """compares authors text channel to the set music channel"""
        if interaction.channel.name == self.music_channel:
            return True

        await interaction.response.send_message("Wrong channel for music commands")
        return False


    async def _in_voice_channel(self, interaction: discord.Interaction):
        """Users have to be in a voice channel""" #TODO fix
        
        try: #checks if the author is in a voice channel
            #interaction.message.author.voice

            interaction.user.voice

        except AttributeError: # user isnt in any voice channel
            await interaction.response.send_message("You are not in a voice channel")
            print("false")
            return False

        return True


    async def _search_youtube(self, *, query): #TODO rewrite to give better results
        """searchs youtube with the query, and returns the url of the top video"""
        query_string = urllib.parse.urlencode({
            'search_query': query
        })

        htm_content = urllib.request.urlopen(
            'https://www.youtube.com/results?' + query_string
        )

        search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
        return 'https://www.youtube.com/watch?v=' + search_results[0] #TODO rewrite to accpect playlists


    async def _play_next_song(self, error=None):
        """figures out what voice channel the user is in, and joins. Then it downloads and encodes and plays from the queue"""
        if os.path.isfile('song.opus'):
            os.remove('song.opus')


        #encase song fails to skip and then finishes
        self.how_many_want_to_skip = 0

        if len(self.q) == 0: #base case
            self._is_playing_song = False
            print('No more songs in queue')
            await self.disconnect(interaction)
            return

        next_url, interaction = self.q.pop()
        if self.loop_enabled:
            self.q.append((next_url, interaction))

        print("before connect")
    
        try: #connect to channel #TODO i think all of this is unneeded
            print("124")
            voice_channel = interaction.user.voice.channel # error is handled eariler
            print("126")
            await voice_channel.connect()
            print("128")
            voice = interaction.guild.voice_client
            print("130")
            await interaction.followup.send(f'**Connected** :drum: to `{str(voice_channel)}`')

        except ClientException: #already connected
            voice = interaction.guild.voice_client

        print("after connect")
        

        self._is_playing_song = True
        print(f'Playing next song: {next_url}')

        with YoutubeDL(self._ydl_opts) as ydl: #download audio

            info_dict = await asyncio.to_thread(ydl.extract_info, next_url, False)
            #check if the link is a playlist
            if info_dict.get('_type', None) != None:
                #call _add_videos_from_playlist function to deal with it
                await self._add_videos_from_playlist(interaction, next_url)

                next_url, interaction = self.q.pop() #since we added a butch of new urls and the current next_url is a playlist
                info_dict = await asyncio.to_thread(None, ydl.extract_info, next_url, False) #new video new metadata

            ydl.download([next_url])

        for file in os.listdir(os.getcwd()):
            if file.endswith('.opus'):
                os.rename(file, 'song.opus')

        voice.play(discord.FFmpegOpusAudio("song.opus", bitrate=192), after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next_song(e), self.client.loop))

        await interaction.followup.send(f"**Playing** :notes: `{info_dict.get('title', None)}` by `{info_dict.get('channel', None)}` - Now!")


    async def _is_video_too_long(self, info_dict):
        #info_dict stores duration in seconds
        print(info_dict.get('duration', None))
        if info_dict.get('duration', None) > 32400:
            return True

        return False


    async def _add_video(self, interaction, video_url, is_playlist=False, add_to_bottom_of_q=True):
        #sees if the video is public
        #with YoutubeDL({'match_filter': yt_dlp.utils.match_filter_func('availability != private'), 'ignore_no_formats_error': True}) as ydl:
        with YoutubeDL(self._ydl_opts) as ydl:
            #make sure video is valid
            info_dict = await asyncio.to_thread(ydl.extract_info, video_url, False)
            print("info_dict got")

            #if video is a playlist
            if info_dict.get('_type', None) != None: #is playlist
                await self._add_videos_from_playlist(interaction, video_url)
                return
        
            #if video is too long
            if await self._is_video_too_long(info_dict):
                await interaction.followup.send('video too long! >:(')
                return
                
        
        
        #if is_playlist:

        if add_to_bottom_of_q: #play or playurl
            self.q.appendleft((video_url, interaction))
                #await interaction.response.send_message(f"**Added** :musical_note: `{video_url}` to queue")

        else: #playnext
            self.q.append((video_url, interaction))
                #await interaction.response.send_message(f"**Added** :musical_note: `{video_url}` to the top of the queue") 


    async def _add_videos_from_playlist(self, interaction: discord.Interaction, playlist_url):
        #extract_flat false so we can take videos out one by one
        await interaction.response.send_message(f'**Added Playlist** :musical_note: `{playlist_url}` to queue')
        
        with YoutubeDL({'extract_flat': False, 'match_filter': yt_dlp.utils.match_filter_func('availability != private'), 'ignore_no_formats_error': True}) as ydl:
            #get the info_dict with all playlist videos
            playlist_info_dict = await asyncio.to_thread(ydl.extract_info, playlist_url, False)

            for index in range(len(playlist_info_dict.get('entries', None))):
                if playlist_info_dict.get('entries')[index].get('uploader') == None:
                    await interaction.followup.send(f'**track {index +1}** :cd: is not public and was not added to the queue')
                    print("private track")
                    continue

                #add video
                await self._add_video(interaction, playlist_info_dict.get('entries')[index].get('webpage_url'), is_playlist=True)
                print("true")


    async def _play_or_add_url(self, interaction, url, add_to_bottom_of_q=True):
        """basic if statement to stop dry code"""
        print("line 222")
        #add video
        if not add_to_bottom_of_q: #play
            await self._add_video(interaction, url)

        else: #playnext
            await self._add_video(interaction, url, add_to_bottom_of_q=False)

        #play video
        if not self._is_playing_song:
            await self._play_next_song(None)


    @app_commands.command(name="play", description="plays a query from Youtube")
    async def play(self, interaction: discord.Interaction, *, query : str, add_to_bottom_of_q: bool = False): 
        print("line 231")
        if not await self._in_voice_channel(interaction):
            return
        
        print("235")

        print(self.music_channel)
        if not await self._is_music_channel(interaction):
            return
        
        print("240")

        url = await self._search_youtube(query=query)
        print("line 243")

        await self._play_or_add_url(interaction, url, add_to_bottom_of_q)
            

    @app_commands.command(name="play-top", description="plays a query from Youtube next")
    async def playtop(self, interaction: discord.Interaction, *, query : str): #TODO unfuse this from play
        await self.play(interaction, query=query, add_to_bottom_of_q = True)


    @app_commands.command(name="play-url", description="plays a Youtube url")
    async def playurl(self, interaction: discord.Interaction, url : str):
        if not await self._in_voice_channel(interaction) or not await self._is_music_channel(interaction):
            return

        #this function HAS TO have a valid url
        if 'https://www.youtube.com/watch?v=' in url or 'https://youtu.be/' in url:
            #link might be valid
            try:
                with YoutubeDL({'extract_flat': True}) as ydl: #download metadata
                    ydl.extract_info(url, False)
            except DownloadError: #if video doesnt exist
                await interaction.response.send_message("Invalid url")
                return

            #video is valid, add to q
            await self._play_or_add_url(interaction, url)


    @app_commands.command(name="pause", description="Pauses track")
    async def pause(self, interaction: discord.Interaction):
        if not await self._in_voice_channel(interaction):
            return
        voice = interaction.guild.voice_client

        if voice.is_playing():
            voice.pause()
            await interaction.response.send_message("**Paused** :pause_button:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name="resume", description="Resumes track")
    async def resume(self, interaction: discord.Interaction):
        if not await self._in_voice_channel(interaction):
            return
        voice = interaction.guild.voice_client

        if voice.is_paused():
            voice.resume()
            await interaction.response.send_message("**Resumed** :arrow_forward:")

        else:
            await interaction.response.send_message("Nothing is paused")


    @app_commands.command(name="force-skip", description="Skips the track")
    async def forceskip(self, interaction: discord.Interaction):
        if not await self._in_voice_channel(interaction):
            return
        voice = interaction.guild.voice_client
        
        if voice.is_playing():
            self.how_many_want_to_skip = 0 #reset counter
            voice.stop()
            await interaction.response.send_message("**Skipped** :fast_forward:")
            asyncio.run_coroutine_threadsafe(self._play_next_song(interaction), self.client.loop) #file io is blocking :(

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name='skip', description='Calls a vote to skip the track')
    async def skip(self, interaction: discord.Interaction):
        if not await self._in_voice_channel(interaction):
            return
        voice = interaction.guild.voice_client

        if voice.is_playing():
            #increase the how_many_want_to_skip
            self.how_many_want_to_skip += 1

            #check if its passed threshold
            voice_channel = interaction.message.author.voice.channel
            threshold = floor((len(voice_channel.members)-1)/2) #-1 for the bot

            if self.how_many_want_to_skip >= threshold: #enough people
                await self.forceskip(interaction)
            
            else: #not enough people
                await interaction.response.send_message(f'**Skipping? ({self.how_many_want_to_skip}/{threshold} people) or use `forceskip`**')

        else:
            await interaction.response.send_message("Nothing is playing")
            return


    @app_commands.command(name="queue", description="Lists the queue")
    async def queue(self, interaction: discord.Interaction):
        tempq = self.q.copy()

        #incase the queue was empty from the start
        if len(tempq) == 0:
            await interaction.response.send_message("The queue is empty")
            return

        #store every element in a string
        index = 0
        output = ""
        while tempq:
            #get the url of the video
            current_url, unused_ctx = tempq.pop()
            with YoutubeDL(self._ydl_opts) as ydl: #download metadata
                info_dict = await asyncio.to_thread(ydl.extract_info, current_url, False)

            output += (f"{index +1}. `{info_dict.get('title', None)}` - `{info_dict.get('duration_string', None)}`\n")
            index += 1

        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)


    @commands.command(name='queue-clear', description='Clears everything in the queue')
    async def queueclear(self, interaction: discord.Interaction):
        self.q.clear()
        await interaction.response.send_message("**Cleared queue** :books:")


    @app_commands.command(name='queue-remove', description='removes a song from the queue based on its track number')
    async def queueremove(self, interaction: discord.Integration, queue_position : int):
        if queue_position > len(self.q) or queue_position < 0:
            await interaction.response.send_message("Input invalid")
            return

        #because of how the remove function works we have to make a copy
        tempq = self.q.copy()

        for index in range(queue_position -1): #so we dont have to save what's popped
            tempq.pop()

        #we should have the url of the track we want to remove
        self.q.remove(tempq.pop())
        await interaction.response.send_message("**Removed from queue** :books:")


    @app_commands.command(name='loop', description='Loops the current song until disabled')
    async def loop(self, interaction: discord.Interaction): #TODO refactor this to put it to disable removing tracks and add it once
        if self.loop_enabled: #disable loop
            self.loop_enabled = False
            await interaction.response.send_message("**Loop Disabled** :repeat:")
            #remove song from queue

        else: #enable loop
            self.loop_enabled = True
            #add current song back into q and disable removing songs from q
            await interaction.response.send_message("**Loop Enabled** :repeat:")



async def setup(client):
    await client.add_cog(Music_Commands(client))