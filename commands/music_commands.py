from collections import deque
from math import floor

import wavelink
import discord
from discord import app_commands
from discord.ext import commands, tasks

class Music_Commands(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        #self.disconnect_timer.start()

        self.song_queue = deque()
        self.is_playing = False 
        self.how_many_want_to_skip = 0
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
        if len(self.song_queue) == 0:
            #queue is empty
            self.is_playing = False
             #disconnect the bot or make a timer or smth
            return
        
        #else we want to keep playing
        await self.play_song()


    async def connect(self, interaction): #TODO add error catching
        if not interaction.guild.voice_client:
            voice: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            await interaction.followup.send(f'**Connected** :drum: to `{interaction.user.voice.channel.name}`')

        else:
            voice: wavelink.Player = interaction.guild.voice_client

        #start disconnect timer
        self.disconnect_timer.start()

        return voice

    
    async def stop_voice_functions(self, voice: discord.VoiceClient):
        print("stop_voice_functions")
        self.song_queue.clear() #wipe all future songs
        print(self.song_queue)
        self.is_playing = False
        await voice.stop()            
        await voice.disconnect()
        self.disconnect_timer.stop()
        print("is playing",self.is_playing)

    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    async def disconnect(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.is_connected():
            await self.stop_voice_functions(voice)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** :guitar:")

        else:
            await interaction.response.send_message("Already disconnected") 

    
    @tasks.loop(seconds=10)
    async def disconnect_timer(self):
        print("currentloop", self.disconnect_timer.current_loop)
        #When a task is started is runs for the first time, which is too fast
        if self.disconnect_timer.current_loop == 0:
            return

        for voice in self.bot.voice_clients:
            print("peps in vc",len(voice.channel.members), "list ->", voice.channel.members)
            if len(voice.channel.members) < 2: #no-one or bot in vc
                await self.stop_voice_functions(voice)
                #await vc.disconnect()
                print("disconnect")
                
        


    async def play_or_add(self, track: wavelink.YouTubeTrack, interaction, add_to_bottom=True):
        """Takes a track and adds it to the queue, and if nothing is playing this sends it to play"""
        #add to queue
        if add_to_bottom:
            self.song_queue.appendleft((track, interaction))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to queue")
        
        else: #playnext
            self.song_queue.append((track, interaction))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to the top of the queue") 

        #if not playing we start playing
        print("is playing",self.is_playing)
        if not self.is_playing:
            await self.play_song()


    async def play_song(self):
        """plays the first song in the queue"""
        self.how_many_want_to_skip = 0 #reset counter

        track, interaction = self.song_queue.pop()

        if self.loop_enabled:
            #add the track back into the front
            self.song_queue.append((track, interaction))


        #connect bot to voice chat
        voice = await self.connect(interaction)

        self.now_playing_dict = track.info
        #play track
        await voice.play(track)
        await interaction.followup.send(f"**Playing** :notes: `{track.title}` by `{track.author}` - Now!")   


    @app_commands.command(name="play", description="plays a Youtube track")#TODO add cool downs for commands
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, *, query: str):
        """Play a song with the given search query."""

        track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        await self.play_or_add(track, interaction)


    @app_commands.command(name="play-next", description="plays a Youtube track after the current one") #TODO add cool downs for commands
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play_next(self, interaction: discord.Interaction, *, query: str):
        """Play a song with the given search query."""

        track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        await self.play_or_add(track, interaction, add_to_bottom=False)


    @app_commands.command(name="pause", description="Pauses track")
    async def pause(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.is_playing():
            await voice.pause()
            await interaction.response.send_message("**Paused** :pause_button:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name="resume", description="Resumes track")
    async def resume(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.is_paused():
            await voice.resume()
            await interaction.response.send_message("**Resumed** :arrow_forward:")

        else:
            await interaction.response.send_message("Nothing is paused")


    @app_commands.command(name="force-skip", description="Skips the track")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def forceskip(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client
        
        if voice.is_playing():
            await voice.stop()
            await interaction.response.send_message("**Skipped** :fast_forward:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name="skip", description="Calls a vote to skip the track")
    async def skip(self, interaction: discord.Interaction): #TODO make a list of people who have voted and wipe on new song
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


    @app_commands.command(name="now-playing", description="Show the playing song")
    async def nowplaying(self, interaction: discord.Interaction):
        if not self.is_playing:
            await interaction.response.send_message("Nothing is playing")
            return

        print("before embed")
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
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
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
            queue_hours, queue_minutes = divmod(minutes, 60)
            embed.set_footer(text=f'Total length {floor(queue_hours)}:{await self.add_zero(floor(queue_minutes))}:{await self.add_zero(floor(queue_seconds))}')
        else:
            embed.set_footer(text=f'Total length {floor((queue_minutes))}:{await self.add_zero(floor(queue_seconds))}')
        
        await interaction.followup.send(embed=embed)


    async def add_zero(self, number):
        """turns 2 seconds to 02"""
        if number < 10:
            return "0" + str(number)

        return str(number)


    @app_commands.command(name='queue-clear', description='Clears everything in the queue')
    async def queueclear(self, interaction: discord.Interaction):
        self.song_queue.clear()
        await interaction.response.send_message("**Cleared queue** :books:")


    @app_commands.command(name='queue-remove', description='Removes a song from the queue based on its track number')
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


    @app_commands.command(name='loop', description='Loops the current song until disabled')
    async def loop(self, interaction: discord.Interaction):
        if not self.is_playing:
            await interaction.response.send_message("Nothing Playing")
            return

        print("interaction",interaction.id)

        if self.loop_enabled: #disable loop
            print("if")
            track, interaction = self.song_queue.pop()
            self.loop_enabled = False
            await interaction.followup.send("**Loop Disabled** :repeat:")

        else: #enable loop
            print("else")
            #add current song to the top of the queue once
            track = await wavelink.YouTubeTrack.search(query=self.now_playing_dict.get('title'), return_first=True)
            self.song_queue.append((track, interaction))
            self.loop_enabled = True
            await interaction.response.send_message("**Loop Enabled** :repeat:")

        print("end of command")






































async def setup(bot):
    await bot.add_cog(Music_Commands(bot))