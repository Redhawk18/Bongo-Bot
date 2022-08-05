from code import interact
from collections import deque
from math import floor
import re

import wavelink
import discord
from discord import ButtonStyle, app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View

import custom_player

class Music_Commands(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.song_queue = deque()
        self.is_playing = False 
        self.playing_interaction:discord.Interaction = None
        self.user_who_want_to_skip:list = []
        self.now_playing_dict:dict = None
        self.loop_enabled = False
        


    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")


    #Lavalink 
    async def cog_load(self):
        self.bot.loop.create_task(self.connect_nodes())


    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="password"
        )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        self.is_playing = True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.player, track: wavelink.Track, reason):
        #old view can cause problems
        await self.playing_message.edit(view=None)

        if len(self.song_queue) == 0: #queue is empty
            self.is_playing = False
            return
        
        #else we want to keep playing
        await self.play_song()


    async def connect(self, interaction):
        if not interaction.guild.voice_client:
            voice: wavelink.Player = await interaction.user.voice.channel.connect(cls=custom_player.Custom_Player)
            await interaction.followup.send(f'**Connected** :drum: to `{interaction.user.voice.channel.name}`')

        else: #already connected
            voice: wavelink.Player = interaction.guild.voice_client

        #start disconnect timer
        if not self.disconnect_timer.is_running():
            self.disconnect_timer.start()

        return voice


    async def is_in_voice(self, interaction: discord.Integration):
        """returns True if the user is in a voice chat"""
        if interaction.user.voice is None: #not in any voice chat
            await interaction.response.send_message("Not in any voice chat")
            return False
        
        return True


    async def get_voice(self, interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice is None: #not connected to voice
            await interaction.response.send_message("Nothing is playing")
            return None

        return voice

    
    async def stop_voice_functions(self, voice: discord.VoiceClient):
        self.song_queue.clear() #wipe all future songs
        self.is_playing = False
        await voice.stop()            
        await voice.disconnect()
        self.disconnect_timer.stop()


    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    async def disconnect(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None:
            return


        if voice.is_connected():
            await self.stop_voice_functions(voice)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** :guitar:")

        else:
            await interaction.response.send_message("Already disconnected") 

    
    @tasks.loop(seconds=10)
    async def disconnect_timer(self):
        #When a task is started is runs for the first time, which is too fast
        if self.disconnect_timer.current_loop == 0:
            return


        for voice in self.bot.voice_clients:
            if len(voice.channel.members) < 2: #no-one or bot in vc
                await self.stop_voice_functions(voice)
                
        
    async def search_track(self, interaction: discord.Interaction, query, add_to_bottom=True):
        if not await self.is_in_voice(interaction): #user is not in voice chat
            return        

        URL_RE = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        if URL_RE.match(query) and "list=" in query: #playlist
            playlist = await wavelink.YouTubePlaylist.search(query=query)
            await self.add_playlist(playlist, interaction)

        else: #normal track
            track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            await self.add_song(track, interaction, add_to_bottom)    


    async def add_song(self, track: wavelink.YouTubeTrack, interaction, add_to_bottom=True):
        """Takes a track and adds it to the queue, and if nothing is playing this sends it to play"""
        #add to queue
        if add_to_bottom:
            self.song_queue.appendleft((track, interaction))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to queue")
        
        else: #playnext
            self.song_queue.append((track, interaction))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to the top of the queue") 

        #if not playing we start playing
        await self.play_if_not()


    async def add_playlist(self, playlist: wavelink.YouTubePlaylist, interaction):
        "Adds each video individually to the queue"
        index = 0
        for track in playlist.tracks:
            self.song_queue.appendleft((track, interaction))
            print(track.info)

            index += 1


        await interaction.response.send_message(f'**Added** :musical_note: Playlist with {index} tracks to the queue')
        await self.play_if_not()


    async def play_if_not(self):
        if not self.is_playing:
            await self.play_song()


    async def play_song(self):
        """plays the first song in the queue"""
        self.user_who_want_to_skip.clear() #reset list

        track, interaction = self.song_queue.pop()

        if self.loop_enabled:
            #add the track back into the front
            self.song_queue.append((track, interaction))


        #connect bot to voice chat
        voice = await self.connect(interaction)

        self.now_playing_dict = track.info
        #play track
        await voice.play(track)
        self.playing_interaction = interaction #to remove the view later
        self.playing_message = await interaction.followup.send(f"**Playing** :notes: `{track.title}` by `{track.author}` - Now!", view=Playing_View(self.bot), wait=True)  


    @app_commands.command(name="play", description="plays a Youtube track")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, *, query: str):
        await self.search_track(interaction, query)


    @app_commands.command(name="play-next", description="plays a Youtube track after the current one")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play_next(self, interaction: discord.Interaction, *, query: str):
        await self.search_track(interaction, query, add_to_bottom=False)


    @app_commands.command(name="pause", description="Pauses track")
    async def pause(self, interaction: discord.Interaction):
        await self.pause_helper(interaction)
        
    async def pause_helper(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None:
            return

        if not voice.is_paused():
            await voice.pause()
            await interaction.response.send_message("**Paused** :pause_button:")

        else:
            await interaction.response.send_message("Already paused")


    @app_commands.command(name="resume", description="Resumes track")
    async def resume(self, interaction: discord.Interaction):
        await self.resume_helper(interaction)

    async def resume_helper(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None:
            return

        if voice.is_paused():
            await voice.resume()
            await interaction.response.send_message("**Resumed** :arrow_forward:")

        else:
            await interaction.response.send_message("Already resumed")


    @app_commands.command(name="force-skip", description="Skips the track")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def forceskip(self, interaction: discord.Interaction):
        await self.forceskip_helper(interaction)

    async def forceskip_helper(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None:
            return
        
        if voice.is_playing():
            await voice.stop()
            await interaction.response.send_message("**Skipped** :track_next:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name="skip", description="Calls a vote to skip the track")
    async def skip(self, interaction: discord.Interaction):
        await self.skip_helper(interaction)

    async def skip_helper(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None:
            return

        if voice.is_playing():
            #check list if the user is the same
            for id in self.user_who_want_to_skip:
                if id == interaction.user.id: #already voted
                    await interaction.response.send_message("You already voted")
                    return

            #add user id to list
            self.user_who_want_to_skip.append(interaction.user.id)

            #check if its passed threshold
            voice_channel = interaction.message.author.voice.channel
            threshold = floor((len(voice_channel.members)-1)/2) #-1 for the bot

            if len(self.user_who_want_to_skip) >= threshold: #enough people
                await self.forceskip_helper(interaction)
            
            else: #not enough people
                await interaction.response.send_message(f'**Skipping? ({len(self.user_who_want_to_skip)}/{threshold} people) or use `forceskip`**')

        else:
            await interaction.response.send_message("Nothing is playing")
            return


    @app_commands.command(name="now-playing", description="Show the playing song")
    async def nowplaying(self, interaction: discord.Interaction):
        await self.nowplaying_helper(interaction)

    async def nowplaying_helper(self, interaction: discord.Interaction):
        if not self.is_playing:
            await interaction.response.send_message("Nothing is playing")
            return

        print(self.now_playing_dict)
        embed = discord.Embed(
            title = "**Now Playing** :notes:",
            url = self.now_playing_dict.get('uri'),
            color = discord.Color.red(),
            description=""
        ) 
        embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/" + self.now_playing_dict.get('identifier') + "/maxresdefault.webp")
        embed.add_field(name="Title", value=self.now_playing_dict.get('title'), inline=False)
        embed.add_field(name="Uploader", value=self.now_playing_dict.get('author'))

        total_seconds = self.now_playing_dict.get('length')/1000
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            embed.add_field(name="Duration", value=f'{floor(hours)}:{await self.add_zero(floor(minutes))}:{await self.add_zero(floor(seconds))}')
        else:
            embed.add_field(name="Duration", value=f'{floor(minutes)}:{await self.add_zero(floor(seconds))}')

        await interaction.response.send_message(embed=embed) 



    @app_commands.command(name="queue", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id)) #TODO followup embed send causes webhook problems
    async def queue(self, interaction: discord.Interaction):
        tempq = self.song_queue.copy()

        #incase the queue was empty from the start
        if len(tempq) == 0:
            await interaction.response.send_message("The queue is empty")
            return
        await interaction.response.send_message("Queue is loading")

        #store every element in a string
        index = 0
        output = ""
        total_seconds = 0
        while tempq:
            #get the url of the video
            track, interaction = tempq.pop()

            minutes, seconds = divmod(track.length, 60)
            if minutes >= 60:
                hours, minutes = divmod(minutes, 60)
                output += (f"{index +1}. `{track.title}` - `{floor(hours)}:{await self.add_zero(floor(minutes))}:{await self.add_zero(floor(seconds))}`\n")
            else:
                output += (f"{index +1}. `{track.title}` - `{floor(minutes)}:{await self.add_zero(floor(seconds))}`\n")

            total_seconds += track.length
            index += 1


        embed = discord.Embed( #5000 character limit
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )
        #figure the length of the queue
        queue_minutes, queue_seconds = divmod(total_seconds, 60)
        if queue_minutes >= 60:
            queue_hours, queue_minutes = divmod(queue_minutes, 60)
            embed.set_footer(text=f'Total length {floor(queue_hours)}:{await self.add_zero(floor(queue_minutes))}:{await self.add_zero(floor(queue_seconds))}')
        else:
            embed.set_footer(text=f'Total length {floor((queue_minutes))}:{await self.add_zero(floor(queue_seconds))}')
        
        await interaction.followup.send(embed=embed)


    async def add_zero(self, number):
        """turns 2 seconds to 02"""
        if number < 10:
            return "0" + str(number)

        return str(number)


    @app_commands.command(name="queue-clear", description="Clears everything in the queue")
    async def queueclear(self, interaction: discord.Interaction):
        self.song_queue.clear()
        await interaction.response.send_message("**Cleared queue** :books:")


    @app_commands.command(name="queue-remove", description="Removes a song from the queue based on its track number")
    async def queueremove(self, interaction: discord.Integration, queue_position : int):
        if queue_position > len(self.q) or queue_position < 0:
            await interaction.response.send_message("Input invalid")
            return

        #because of how the remove function works we have to make a copy
        tempq = self.song_queue.copy()

        for index in range(queue_position -1): #so we dont have to save what's popped
            tempq.pop()

        #we should have the url of the track we want to remove
        self.song_queue.remove(tempq.pop())
        await interaction.response.send_message("**Removed from queue** :books:")


    @app_commands.command(name="loop", description="Loops the current song until disabled")
    async def loop(self, interaction: discord.Interaction):
        await self.loop_helper(interaction)

    async def loop_helper(self, interaction: discord.Interaction):
        if not self.is_playing:
            await interaction.response.send_message("Nothing Playing")
            return

        if self.loop_enabled: #disable loop
            track, interaction = self.song_queue.pop()
            self.loop_enabled = False
            await interaction.followup.send("**Loop Disabled** :repeat:")

        else: #enable loop
            #add current song to the top of the queue once
            track = await wavelink.YouTubeTrack.search(query=self.now_playing_dict.get('title'), return_first=True)
            self.song_queue.append((track, interaction))
            self.loop_enabled = True
            await interaction.response.send_message("**Loop Enabled** :repeat:")


    @app_commands.command(name="volume", description="Sets the volume of the player, max is 150")
    async def volume(self, interaction: discord.Interaction, percent: float):
        if percent <= 0 or percent > 150:
            await interaction.response.send_message("Invalid input")
            return

        #turn percent into a float between 0-1.5
        volume = percent/100

        voice = await self.get_voice(interaction)
        if voice is None:
            return

        if voice.is_connected():
            await voice.set_volume(volume, seek=True)
            await interaction.response.send_message(f'**Volume** :loud_sound: changed to {percent}%')
        
        else:
            await interaction.response.send_message("Not connected to voice chat")



async def setup(bot):
    await bot.add_cog(Music_Commands(bot))


class Playing_View(View):
    """Hold the views for the playing output"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot


    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="⏸")
    async def pause_callback(self, interaction, button):
        await self.bot.get_cog("Music_Commands").pause_helper(interaction)


    @discord.ui.button(label="Resume", style=discord.ButtonStyle.gray, emoji="▶️")
    async def resume_callback(self, interaction, button):
        await self.bot.get_cog("Music_Commands").resume_helper(interaction)  


    @discord.ui.button(label="Skip", style=discord.ButtonStyle.gray, emoji="⏭")
    async def skip_callback(self, interaction, button):    
        await self.bot.get_cog("Music_Commands").skip_helper(interaction)


    @discord.ui.button(label="Now Playing", style=discord.ButtonStyle.gray, emoji="🎶")
    async def now_playing_callback(self, interaction, button):
        await self.bot.get_cog("Music_Commands").nowplaying_helper(interaction)


    @discord.ui.button(label="Loop", style=discord.ButtonStyle.gray, emoji="🔁")
    async def loop_callback(self, interaction, button):
        await self.bot.get_cog("Music_Commands").loop_helper(interaction)
