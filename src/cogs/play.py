import logging
import re

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

from custom_player import Custom_Player
from playing_view import Playing_View
from utilities import able_to_use_commands, edit_view_message,get_milliseconds_from_string

log = logging.getLogger(__name__)

class Play(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        log.info(f'Lavalink Connected')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        log.info(f'Now playing "{payload.track.title}" name: {payload.player.guild.name}, id: {payload.player.guild.id}')
        self.bot.variables_for_guilds[payload.player.guild.id].is_playing = True

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        log.info(f'Finished playing "{payload.track.title}" name: {payload.player.guild.name}, id: {payload.player.guild.id}')
        #old view can cause problems
        await edit_view_message(self.bot, payload.player.guild.id, None)

        if len(self.bot.variables_for_guilds[payload.player.guild.id].song_queue) == 0: #queue is empty
            self.bot.variables_for_guilds[payload.player.guild.id].is_playing = False
            return

        #else we want to keep playing
        await self.play_song(payload.player.guild.id)

    async def connect(self, interaction):
        if not interaction.guild.voice_client:
            voice: Custom_Player = await interaction.user.voice.channel.connect(cls=Custom_Player)
            await interaction.followup.send(f'**Connected** 🥁 to `{interaction.user.voice.channel.name}`')

        else: #already connected
            voice: Custom_Player = interaction.guild.voice_client

        return voice

    async def get_voice_from_id(self, guild_id:int) -> discord.VoiceProtocol:
        voice: Custom_Player = self.bot.get_guild(guild_id).voice_client

        return voice

    @app_commands.command(name="play", description="plays a Youtube track, start time need to formated with colons")
    @app_commands.describe(query="What to search youtube for", play_next="If this track should be put at the front of the queue", start_time="time stamp to start the video at, for example 1:34 or 1:21:19")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def play(self, interaction: discord.Interaction, *, query: str, play_next: bool=False, start_time: str=None):
        #locked channel is full
        if len(interaction.user.voice.channel.members) == interaction.user.voice.channel.user_limit: #== because admin can drag bot into channel
            await interaction.response.send_message("Locked voice channel is at max capacity")
            return

        if not interaction.user.voice.channel.permissions_for(interaction.guild.me).connect is True:
            await interaction.response.send_message("Does not have permission to connect")
            return

        if start_time is not None: #parser
            start_time = await get_milliseconds_from_string(start_time, interaction)
            if start_time == -1: #time code was invalid
                return

        await self.search_track(interaction, query, play_next, start_time)

    async def search_track(self, interaction: discord.Interaction, query, play_next, start):
        if not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing, self.bot.variables_for_guilds[interaction.guild_id].music_channel_id, self.bot.variables_for_guilds[interaction.guild_id].music_role_id): #user is not in voice chat
            return

        URL_RE = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        if URL_RE.match(query) and "list=" in query: #playlist
            try:
                playlist = await wavelink.YouTubePlaylist.search(query)
            except: #playlist not found
                await interaction.response.send_message("playlist does not exist")
                return

            await self.add_playlist(playlist, interaction)

        else: #normal track
            try:
                track = await wavelink.YouTubeTrack.search(query, return_first=True)
            except: #video not found
                await interaction.response.send_message("video does not exist")
                return

            await self.add_song(track, interaction, play_next, start)

    async def add_song(self, track: wavelink.YouTubeTrack, interaction: discord.Interaction, play_next, start):
        """Takes a track and adds it to the queue, and if nothing is playing this sends it to play"""
        #add to queue
        if play_next:
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.append((track, interaction.channel, start))
            await interaction.response.send_message(f"**Added** 🎵 `{track.uri}` to the top of the queue")

        else: #add to top
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.appendleft((track, interaction.channel, start))
            await interaction.response.send_message(f"**Added** 🎵 `{track.uri}` to queue")

        #if not playing we start playing
        await self.play_if_not(interaction, interaction.guild_id)

    async def add_playlist(self, playlist: wavelink.YouTubePlaylist, interaction):
        """Adds each video individually to the queue"""
        index = 0
        for track in playlist.tracks:
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.appendleft((track, interaction.channel, None))

            index += 1

        await interaction.response.send_message(f'**Added** 🎵 playlist with {index} tracks to the queue')
        await self.play_if_not(interaction, interaction.guild_id)

    async def play_if_not(self, interaction, guild_id):
        await self.connect(interaction)
        if not self.bot.variables_for_guilds[guild_id].is_playing:
            await self.play_song(guild_id)

    async def play_song(self, guild_id):
        """plays the first song in the queue"""
        self.bot.variables_for_guilds[guild_id].user_who_want_to_skip.clear() #reset list
        track, channel, start = self.bot.variables_for_guilds[guild_id].song_queue.pop()

        if self.bot.variables_for_guilds[guild_id].loop_enabled:
            #add the track back into the front
            self.bot.variables_for_guilds[guild_id].song_queue.append((track, channel, start))

        self.bot.variables_for_guilds[guild_id].now_playing_track = track

        #connect bot to voice chat
        voice = await self.get_voice_from_id(channel.guild.id)

        #play track
        await voice.play(track, start=start, volume=self.bot.variables_for_guilds[guild_id].volume)
        playing_view = Playing_View(self.bot)
        playing_view_msg: discord.Message = await channel.send(f'**Playing** 🎶 `{track.title}` by `{track.author}` - Now!', view=playing_view)

        self.bot.variables_for_guilds[guild_id].playing_view = playing_view
        self.bot.variables_for_guilds[guild_id].playing_view_channel_id = channel.id
        self.bot.variables_for_guilds[guild_id].playing_view_message_id = playing_view_msg.id

async def setup(bot):
    await bot.add_cog(Play(bot))
