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
        pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player: wavelink.Player = payload.player

        if player.queue:
            track = await player.queue.get_wait()
            await player.play(track)

    async def connect(self, interaction):
        if not interaction.guild.voice_client:
            voice: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            await interaction.followup.send(f'**Connected** 🥁 to `{interaction.user.voice.channel.name}`')

        else: #already connected
            voice: wavelink.Player = interaction.guild.voice_client

        return voice

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

        await self.search_for_track(interaction, query, next, start_time)

    async def search_for_track(self, interaction: discord.Interaction, query: str, is_next: bool, start_time: int):
        tracks: wavelink.YouTubePlaylist | list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            # Do something
            print(tracks)
            return

        player = await self.connect(interaction)
        await interaction.response.send_message("message")

        #print(tracks)
        print(player.is_connected())
        await self.connect(interaction)
        print(player.is_connected())

        if isinstance(tracks, wavelink.YouTubePlaylist):
            for track in tracks.tracks:
                player.queue.put(track)
        else:
            player.queue.put(tracks[0])
        
        await player.play(player.queue.get())


async def setup(bot):
    await bot.add_cog(Play(bot))
