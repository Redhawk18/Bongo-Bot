import logging
import re

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

from playing_view import Playing_View
from utilities import able_to_use_commands, edit_view_message, get_milliseconds_from_string

log = logging.getLogger(__name__)

class Play(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        log.info(f'Now playing "{payload.track.title}" name: {payload.player.guild.name}, id: {payload.player.guild.id}')
        playing_view = Playing_View(self.bot)
        playing_view_msg: discord.Message = await self.bot.cache[payload.player.guild.id].playing_view_channel.send(f'**Playing** 🎶 `{payload.track.title}` by `{payload.track.author}` - Now!', view=playing_view)

        self.bot.cache[payload.player.guild.id].playing_view = playing_view
        self.bot.cache[payload.player.guild.id].playing_view_message_id = playing_view_msg.id

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        log.info(f'Finished playing "{payload.track.title}" name: {payload.player.guild.name}, id: {payload.player.guild.id}')
        await edit_view_message(self.bot, payload.player.guild.id, None)

    async def connect(self, interaction) -> wavelink.Player:
        if interaction.guild.voice_client: #already connected
            await interaction.followup.send(f'**Connected** 🥁 to `{interaction.user.voice.channel.name}`')
            player: wavelink.Player = interaction.guild.voice_client

        else: 
            player: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)

        return player

    @app_commands.command(name="play", description="plays a Youtube track, start time need to formated with colons")
    @app_commands.describe(query="What to search youtube for", 
    next="If this track should be put at the front of the queue",
    start_time="time stamp to start the video at, for example 1:34 or 1:21:19")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def play(self, interaction: discord.Interaction, *, query: str, next: bool=False, start_time: str=None):
        #locked channel is full
        # if len(interaction.user.voice.channel.members) == interaction.user.voice.channel.user_limit: #== because admin can drag bot into channel
        #     await interaction.response.send_message("Locked voice channel is at max capacity")
        #     return

        # if not interaction.user.voice.channel.permissions_for(interaction.guild.me).connect is True:
        #     await interaction.response.send_message("Does not have permission to connect")
        #     return

        if start_time is not None: #parser
            start_time = await get_milliseconds_from_string(start_time, interaction)
            if start_time == -1: #time code was invalid
                return

        tracks: wavelink.YouTubePlaylist | list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            return
        
        player: wavelink.player = await self.add_to_queue(interaction, next, tracks)
        player.autoplay = True

        if player.is_playing(): # busy
            return

        track = player.queue.get()
        await player.play(track, start=start_time, volume=self.bot.cache[interaction.guild_id].volume, populate=True)

        self.bot.cache[interaction.guild_id].playing_view_channel = interaction.channel

    async def add_to_queue(self, interaction: discord.Interaction, next: bool, tracks: wavelink.YouTubePlaylist | list[wavelink.YouTubeTrack]) -> wavelink.Player:
        player: wavelink.Player

        if isinstance(tracks, wavelink.YouTubePlaylist):
            await interaction.response.send_message(f'Added 🎶 playlist `{tracks.tracks.uri}` to queue')
            player = await self.connect(interaction)
            if next:
                for track in reversed(tracks.tracks):
                    player.queue.put_at_front(track)

            else:
                for track in tracks.tracks:
                    player.queue.put(track)

        else:
            await interaction.response.send_message(f'Added 🎵 `{tracks[0].uri}` to queue')
            player = await self.connect(interaction)
            if next:
                player.queue.put_at_front(tracks[0])

            else:
                player.queue.put(tracks[0])
            

        
        return player

async def setup(bot):
    await bot.add_cog(Play(bot))
