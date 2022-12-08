import re

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

from custom_player import Custom_Player
from playing_view import Playing_View
from utilities import able_to_use_commands, get_milliseconds_from_string

class Play(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

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
        print(f'Now playing "{track.title}" in "{player.guild.name}" {player.guild.id}')
        self.bot.variables_for_guilds[player.guild.id].is_playing = True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Custom_Player, track: wavelink.Track, reason):
        print(f'Finished playing "{track.title}" in "{player.guild.name}" {player.guild.id}')
        #old view can cause problems
        await self.delete_view(player.guild.id)

        if len(self.bot.variables_for_guilds[player.guild.id].song_queue) == 0: #queue is empty
            self.bot.variables_for_guilds[player.guild.id].is_playing = False
            return

        #else we want to keep playing
        await self.play_song(player.guild.id)

    async def connect(self, interaction):
        if not interaction.guild.voice_client:
            voice: Custom_Player = await interaction.user.voice.channel.connect(cls=Custom_Player)
            await interaction.followup.send(f'**Connected** :drum: to `{interaction.user.voice.channel.name}`')

        else: #already connected
            voice: Custom_Player = interaction.guild.voice_client

        return voice

    async def delete_view(self, guild_id):
        playing_view = self.bot.get_channel(self.bot.variables_for_guilds[guild_id].playing_view_channel_id).get_partial_message(self.bot.variables_for_guilds[guild_id].playing_view_message_id)
        await playing_view.delete()

    @app_commands.command(name="play", description="plays a Youtube track, start time need to formated with colons")
    @app_commands.describe(query="What to search youtube for", play_next="If this track should be put at the front of the queue", start_time="time stamp to start the video at, for example 1:34 or 1:21:19")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def play(self, interaction: discord.Interaction, *, query: str, play_next: bool=False, start_time: str=None):
        if start_time is not None: #parser
            start_time = await get_milliseconds_from_string(start_time, interaction)
            if start_time == -1: #time code was invalid
                return

        await self.search_track(interaction, query, play_next, start_time)

    async def search_track(self, interaction: discord.Interaction, query, play_next, start):
        if not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing, self.bot.variables_for_guilds[interaction.guild_id].music_channel_id): #user is not in voice chat
            return

        URL_RE = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        if URL_RE.match(query) and "list=" in query: #playlist
            try:
                playlist = await wavelink.YouTubePlaylist.search(query=query)
            except wavelink.LoadTrackError: #playlist not found
                await interaction.response.send_message("playlist does not exist")
                return
            
            await self.add_playlist(playlist, interaction)

        else: #normal track
            try:
                track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            except IndexError: #video not found
                await interaction.response.send_message("video does not exist")
                return
                
            await self.add_song(track, interaction, play_next, start)

    async def add_song(self, track: wavelink.YouTubeTrack, interaction: discord.Interaction, play_next, start):
        """Takes a track and adds it to the queue, and if nothing is playing this sends it to play"""
        #add to queue
        if play_next:
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.append((track, interaction, start))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to the top of the queue")

        else: #add to top
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.appendleft((track, interaction, start))
            await interaction.response.send_message(f"**Added** :musical_note: `{track.uri}` to queue")

        #if not playing we start playing
        await self.play_if_not(interaction.guild_id)

    async def add_playlist(self, playlist: wavelink.YouTubePlaylist, interaction):
        """Adds each video individually to the queue"""
        index = 0
        for track in playlist.tracks:
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.appendleft((track, interaction, None))

            index += 1

        await interaction.response.send_message(f'**Added** :musical_note: Playlist with {index} tracks to the queue')
        await self.play_if_not(interaction.guild_id)

    async def play_if_not(self, guild_id):
        if not self.bot.variables_for_guilds[guild_id].is_playing:
            await self.play_song(guild_id)

    async def play_song(self, guild_id):
        """plays the first song in the queue"""
        self.bot.variables_for_guilds[guild_id].user_who_want_to_skip.clear() #reset list
        track, interaction, start = self.bot.variables_for_guilds[guild_id].song_queue.pop()

        if self.bot.variables_for_guilds[guild_id].loop_enabled:
            #add the track back into the front
            self.bot.variables_for_guilds[guild_id].song_queue.append((track, interaction, start))

        #connect bot to voice chat
        voice = await self.connect(interaction)

        self.bot.variables_for_guilds[guild_id].now_playing_track = track
        #play track
        
        await voice.play(track, start=start, volume=self.bot.variables_for_guilds[interaction.guild_id].volume)
        playing_message = await interaction.followup.send(f"**Playing** :notes: `{track.title}` by `{track.author}` - Now!", wait=True)
        view = await playing_message.channel.send(view=Playing_View(self.bot))

        self.bot.variables_for_guilds[guild_id].playing_view_channel_id = playing_message.channel.id
        self.bot.variables_for_guilds[guild_id].playing_view_message_id = view.id

async def setup(bot):
    await bot.add_cog(Play(bot))
