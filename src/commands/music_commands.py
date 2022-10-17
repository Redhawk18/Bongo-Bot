from collections import defaultdict
from math import ceil, floor
import re

import discord
from discord import app_commands
from discord.ext import commands, tasks
import wavelink

from custom_player import Custom_Player
import server_infomation

class Music_Commands(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.severs_variables = defaultdict(server_infomation.Server_Infomation) 


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
    async def on_wavelink_track_start(self, player: Custom_Player, track: wavelink.Track):
        print(f'Now playing "{track.title}" in guild {player.guild.id}')
        self.severs_variables[player.guild.id].is_playing = True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Custom_Player, track: wavelink.Track, reason):
        print(f'Finished playing "{track.title}" in guild {player.guild.id}')
        #old view can cause problems
        await self.delete_view(player.guild.id)

        if len(self.severs_variables[player.guild.id].song_queue) == 0: #queue is empty
            self.severs_variables[player.guild.id].is_playing = False
            return

        #else we want to keep playing
        await self.play_song(player.guild.id)


    async def connect(self, interaction):
        if not interaction.guild.voice_client:
            voice: Custom_Player = await interaction.user.voice.channel.connect(cls=Custom_Player)
            await interaction.followup.send(f'**Connected** :drum: to `{interaction.user.voice.channel.name}`')

        else: #already connected
            voice: Custom_Player = interaction.guild.voice_client

        #start disconnect timer
        if not self.disconnect_timer.is_running():
            self.disconnect_timer.start()

        return voice


    async def able_to_use_commands(self, interaction: discord.Interaction):
        """returns True if the user is mets all conditions to use playing commands"""
        if interaction.user.voice is None: #not in any voice chat
            await interaction.response.send_message("Not in any voice chat")
            return False

        if interaction.user.voice.deaf or interaction.user.voice.self_deaf: #deafen
            await interaction.response.send_message("Deafed users can not use playing commands")
            return False

        voice = interaction.guild.voice_client
        if voice is not None:
            if voice.channel.id != interaction.user.voice.channel.id: #bot is in a different voice chat than user
                if self.severs_variables[interaction.guild_id].is_playing: #bot is busy
                    await interaction.response.send_message("Not in the same voice channel")
                    return False

                elif not self.severs_variables[interaction.guild_id].is_playing: #bot is idling
                    await voice.disconnect()
                    return True

        return True


    async def get_voice(self, interaction):
        voice: Custom_Player = interaction.guild.voice_client

        if voice is None: #not connected to voice
            await interaction.response.send_message("Nothing is playing")
            return None

        return voice


    async def stop_voice_functions(self, voice: discord.VoiceClient): #FIXME 
        self.severs_variables[voice.guild.id].song_queue.clear() #wipe all future songs
        self.severs_variables[voice.guild.id].is_playing = False
        await self.delete_view(voice.guild.id)
        await voice.stop()
        await voice.disconnect()
        self.disconnect_timer.stop()


    async def delete_view(self, guild_id):
        playing_view = self.bot.get_channel(self.severs_variables[guild_id].playing_view_channel_id).get_partial_message(self.severs_variables[guild_id].playing_view_message_id)
        await playing_view.delete()


    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    async def disconnect(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None or not await self.able_to_use_commands(interaction):
            return

        if voice.is_connected():
            await self.stop_voice_functions(voice)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** :guitar:")

        else:
            await interaction.response.send_message("Already disconnected")


    @tasks.loop(minutes=10)
    async def disconnect_timer(self):
        #When a task is started is runs for the first time, which is too fast
        if self.disconnect_timer.current_loop == 0:
            return

        for voice in self.bot.voice_clients:
            if len(voice.channel.members) < 2: #no one in voice
                await self.stop_voice_functions(voice)


    async def get_milliseconds_from_string(self, time_string: str, interaction: discord.Interaction):
        "takes a time string and returns the time in milliseconds `1:34` -> `94000`, errors return `-1`"
        TIME_RE = re.compile("^[0-5]?\d:[0-5]?\d:[0-5]\d|[0-5]?\d:[0-5]\d|\d+$")
        if not TIME_RE.match(time_string):
            await interaction.response.send_message("Invalid time stamp")
            return -1

        list_of_units = [int(x) for x in time_string.split(":")]

        list_of_units.reverse() #makes time more predictable to deal with
        total_seconds = 0
        if len(list_of_units) == 3: #hours
            total_seconds += (list_of_units[2] * 3600) #seconds in an hour

        if len(list_of_units) == 2: #minutes
            total_seconds += (list_of_units[1] * 60)

        total_seconds += list_of_units[0] #total seconds

        return (total_seconds * 1000) #turn into milliseconds


    @app_commands.command(name="play", description="plays a Youtube track, start time need to formated with colons")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, *, query: str, play_next: bool=False, start_time: str=None):
        if start_time is not None: #parser
            start_time = await self.get_milliseconds_from_string(start_time, interaction)
            if start_time == -1: #time code was invalid
                return

        #print("play", query, play_next, start_time)
        await self.search_track(interaction, query, add_to_bottom=True, start=start_time)


    async def search_track(self, interaction: discord.Interaction, query, add_to_bottom=True, start=None, end=None):
        #print("search_track", query, add_to_bottom, start)
        if not await self.able_to_use_commands(interaction): #user is not in voice chat
            return

        URL_RE = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        if URL_RE.match(query) and "list=" in query: #playlist
            playlist = await wavelink.YouTubePlaylist.search(query=query)
            await self.add_playlist(playlist, interaction)

        else: #normal track
            track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            await self.add_song(track, interaction, add_to_bottom, start=start, end=end)


    async def add_song(self, track: wavelink.YouTubeTrack, interaction: discord.Interaction, add_to_bottom=True, start=None, end=None):
        #print("add_song", add_to_bottom, start)
        """Takes a track and adds it to the queue, and if nothing is playing this sends it to play"""

        #add to queue
        if add_to_bottom:
            self.severs_variables[interaction.guild_id].song_queue.appendleft((track, interaction, start, end))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to queue")

        else: #add to top
            self.severs_variables[interaction.guild_id].song_queue.append((track, interaction, start, end))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to the top of the queue")

        #if not playing we start playing
        await self.play_if_not(interaction.guild_id)


    async def add_playlist(self, playlist: wavelink.YouTubePlaylist, interaction):
        "Adds each video individually to the queue"
        index = 0
        for track in playlist.tracks:
            self.severs_variables[interaction.guild_id].song_queue.appendleft((track, interaction, None, None))

            index += 1


        await interaction.response.send_message(f'**Added** :musical_note: Playlist with {index} tracks to the queue')
        await self.play_if_not(interaction.guild_id)


    async def play_if_not(self, guild_id):
        if not self.severs_variables[guild_id].is_playing:
            await self.play_song(guild_id)


    async def play_song(self, guild_id):
        """plays the first song in the queue"""
        self.severs_variables[guild_id].user_who_want_to_skip.clear() #reset list
        track, interaction, start, end = self.severs_variables[guild_id].song_queue.pop() #FIXME remove end

        if self.severs_variables[guild_id].loop_enabled:
            #add the track back into the front
            self.severs_variables[guild_id].song_queue.append((track, interaction, start, end))

        #connect bot to voice chat
        voice = await self.connect(interaction)

        self.severs_variables[guild_id].now_playing_dict = track.info
        #play track
        
        await voice.play(track, start=start)
        playing_message = await interaction.followup.send(f"**Playing** :notes: `{track.title}` by `{track.author}` - Now!", wait=True)
        view = await playing_message.channel.send(view=Playing_View(self.bot))

        self.severs_variables[guild_id].playing_view_channel_id = playing_message.channel.id
        self.severs_variables[guild_id].playing_view_message_id = view.id


    @app_commands.command(name="pause", description="Pauses track")
    async def pause(self, interaction: discord.Interaction):
        await self.pause_helper(interaction)

    async def pause_helper(self, interaction: discord.Interaction):
        voice = await self.get_voice(interaction)
        if voice is None or not await self.able_to_use_commands(interaction):
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
        if voice is None or not await self.able_to_use_commands(interaction):
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
        if voice is None or not await self.able_to_use_commands(interaction):
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
        if voice is None or not await self.able_to_use_commands(interaction):
            return

        if voice.is_playing():
            #check list if the user is the same
            for id in self.severs_variables[interaction.guild_id].user_who_want_to_skip:
                if id == interaction.user.id: #already voted
                    await interaction.response.send_message("You already voted")
                    return

            #add user id to list
            self.severs_variables[interaction.guild_id].user_who_want_to_skip.append(interaction.user.id)

            #check if its passed threshold
            voice_channel = interaction.user.voice.channel
            threshold = ceil((len(voice_channel.members)-1)/2) #-1 for the bot

            if len(self.severs_variables[interaction.guild_id].user_who_want_to_skip) >= threshold: #enough people
                await self.forceskip_helper(interaction)

            else: #not enough people
                await interaction.response.send_message(f'**Skipping? ({len(self.user_who_want_to_skip)}/{threshold} votes needed) or use `forceskip`**')

        else:
            await interaction.response.send_message("Nothing is playing")
            return


    @app_commands.command(name="now-playing", description="Show the playing song")
    async def nowplaying(self, interaction: discord.Interaction):
        await self.nowplaying_helper(interaction)

    async def nowplaying_helper(self, interaction: discord.Interaction):
        if not self.severs_variables[interaction.guild_id].is_playing:
            await interaction.response.send_message("Nothing is playing")
            return

        embed = discord.Embed(
            title = "**Now Playing** :notes:",
            url = self.severs_variables[interaction.guild_id].now_playing_dict.get('uri'),
            color = discord.Color.red(),
            description=""
        )
        embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/" + self.severs_variables[interaction.guild_id].now_playing_dict.get('identifier') + "/maxresdefault.webp")
        embed.add_field(name="Title", value=self.severs_variables[interaction.guild_id].now_playing_dict.get('title'), inline=False)
        embed.add_field(name="Uploader", value=self.severs_variables[interaction.guild_id].now_playing_dict.get('author'))

        total_seconds = self.severs_variables[interaction.guild_id].now_playing_dict.get('length')/1000
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
        if len(self.severs_variables[interaction.guild_id].song_queue) == 0: #incase the queue was empty from the start
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        tempq = self.severs_variables[interaction.guild_id].song_queue.copy()

        #store every element in a string
        index = 0
        output = ""
        total_seconds = 0
        while tempq:
            #get the url of the video
            track, player_interaction, start, end = tempq.pop() #FIXME

            minutes, seconds = divmod(track.length, 60)
            if minutes >= 60:
                hours, minutes = divmod(minutes, 60)
                output += (f"{index +1}. `{track.title}` - `{floor(hours)}:{await self.add_zero(floor(minutes))}:{await self.add_zero(floor(seconds))}`\n")
            else:
                output += (f"{index +1}. `{track.title}` - `{floor(minutes)}:{await self.add_zero(floor(seconds))}`\n")

            total_seconds += track.length
            index += 1
            if index > 50: #giant queues have trouble loading
                break


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

        await interaction.edit_original_response(content="", embed=embed)


    async def add_zero(self, number):
        """turns 2 seconds to 02"""
        if number < 10:
            return "0" + str(number)

        return str(number)


    @app_commands.command(name="queue-clear", description="Clears everything in the queue")
    async def queueclear(self, interaction: discord.Interaction):
        self.severs_variables[interaction.guild_id].song_queue.clear()
        await interaction.response.send_message("**Cleared queue** :books:")


    @app_commands.command(name="queue-remove", description="Removes a song from the queue based on its track number")
    async def queueremove(self, interaction: discord.Interaction, queue_position : int):
        if queue_position > len(self.q) or queue_position < 0:
            await interaction.response.send_message("Input invalid")
            return

        #because of how the remove function works we have to make a copy
        tempq = self.severs_variables[interaction.guild_id].song_queue.copy()

        for index in range(queue_position -1): #so we dont have to save what's popped
            tempq.pop()

        #we should have the url of the track we want to remove
        self.severs_variables[interaction.guild_id].song_queue.remove(tempq.pop())
        await interaction.response.send_message("**Removed from queue** :books:")


    @app_commands.command(name="loop", description="Loops the current song until disabled")
    async def loop(self, interaction: discord.Interaction):
        await self.loop_helper(interaction)

    async def loop_helper(self, interaction: discord.Interaction):
        if not await self.able_to_use_commands(interaction):
            return

        if not self.severs_variables[interaction.guild_id].is_playing:
            await interaction.response.send_message("Nothing Playing")
            return

        #FIXME fix all of this
        if self.severs_variables[interaction.guild_id].loop_enabled: #disable loop
            track, player_interaction, start, end = self.severs_variables[interaction.guild_id].song_queue.pop()
            self.severs_variables[interaction.guild_id].loop_enabled = False
            await interaction.response.send_message("**Loop Disabled** :repeat:")

        else: #enable loop
            #add current song to the top of the queue once
            track = await wavelink.YouTubeTrack.search(query=self.severs_variables[interaction.guild_id].now_playing_dict.get('title'), return_first=True)
            self.severs_variables[interaction.guild_id].song_queue.append((track, interaction, None, None))
            self.severs_variables[interaction.guild_id].loop_enabled = True
            await interaction.response.send_message("**Loop Enabled** :repeat:")


    @app_commands.command(name="volume", description="Sets the volume of the player, max is 150")
    async def volume(self, interaction: discord.Interaction, percent: app_commands.Range[float, 0, 150]):
        #turn percent into a float between 0-1.5
        volume = percent/100

        voice = await self.get_voice(interaction)
        if voice is None or not await self.able_to_use_commands(interaction):
            return

        if voice.is_connected():
            await voice.set_volume(volume, seek=True)
            await interaction.response.send_message(f'**Volume** :loud_sound: changed to {percent}%')

        else:
            await interaction.response.send_message("Not connected to voice chat")



async def setup(bot):
    await bot.add_cog(Music_Commands(bot))


class Playing_View(discord.ui.View):
    """The view for the playing output"""
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
