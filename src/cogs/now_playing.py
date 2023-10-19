import discord
from discord import app_commands
from discord.ext import commands
import wavelink

import bongo_bot


class Now_Playing(commands.Cog):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @app_commands.command(name="now-playing", description="Show the playing song")
    @app_commands.guild_only()
    async def now_playing(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Playable = await self.bot.get_player(interaction)
        track = player.current

        if not track:
            await interaction.response.send_message("Nothing is playing")
            return

        embed = discord.Embed(
            title="**Now Playing** 🎶",
            url=track.uri,
            color=discord.Color.red(),
            description="",
        )
        embed.set_thumbnail(url=track.artwork)
        embed.add_field(name="Title", value=track.title, inline=False)
        embed.add_field(name="Uploader", value=track.author)

        total_seconds = track.length
        voice_position = player.position

        if track.is_stream:
            embed.add_field(name="Duration", value="Livestream")

        else:
            embed.add_field(
                name="Duration",
                value=f"{self.bot.milliseconds_to_timestring(voice_position)}/{self.bot.milliseconds_to_timestring(total_seconds)}",
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Now_Playing(bot))
