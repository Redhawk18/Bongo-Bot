from math import floor

import discord
from discord import app_commands
from discord.ext import commands

from utilities import add_zero

class Now_Playing(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="now-playing", description="Show the playing song")
    async def now_playing(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not self.bot.variables_for_guilds[interaction.guild_id].is_playing:
            await interaction.response.send_message("Nothing is playing")
            return

        embed = discord.Embed(
            title = "**Now Playing** :notes:",
            url = self.bot.variables_for_guilds[interaction.guild_id].now_playing_track.uri,
            color = discord.Color.red(),
            description=""
        )
        embed.set_thumbnail(url="https://i.ytimg.com/vi_webp/" + self.bot.variables_for_guilds[interaction.guild_id].now_playing_track.identifier + "/maxresdefault.webp")
        embed.add_field(name="Title", value=self.bot.variables_for_guilds[interaction.guild_id].now_playing_track.title, inline=False)
        embed.add_field(name="Uploader", value=self.bot.variables_for_guilds[interaction.guild_id].now_playing_track.author)

        total_seconds = self.bot.variables_for_guilds[interaction.guild_id].now_playing_track.length
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            embed.add_field(name="Duration", value=f'{floor(hours)}:{await add_zero(floor(minutes))}:{await add_zero(floor(seconds))}')
        else:
            embed.add_field(name="Duration", value=f'{floor(minutes)}:{await add_zero(floor(seconds))}')

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Now_Playing(bot))
    