import discord
from discord import app_commands
from discord.ext import commands

from utilities import seconds_to_timestring

class Now_Playing(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="now-playing", description="Show the playing song")
    @app_commands.guild_only()
    async def now_playing(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not self.bot.cache[interaction.guild_id].is_playing:
            await interaction.response.send_message("Nothing is playing")
            return

        voice_position = (await self.bot.get_voice(interaction.guild_id, interaction)).position / 1000

        embed = discord.Embed(
            title = "**Now Playing** 🎶",
            url = self.bot.cache[interaction.guild_id].now_playing_track.uri,
            color = discord.Color.red(),
            description=""
        )
        embed.set_thumbnail(url=self.bot.cache[interaction.guild_id].now_playing_track.thumbnail)
        embed.add_field(name="Title", value=self.bot.cache[interaction.guild_id].now_playing_track.title, inline=False)
        embed.add_field(name="Uploader", value=self.bot.cache[interaction.guild_id].now_playing_track.author)

        total_seconds = self.bot.cache[interaction.guild_id].now_playing_track.length / 1000
        print("total_seconds",total_seconds)

        if self.bot.cache[interaction.guild_id].now_playing_track.is_stream:
            embed.add_field(name="Duration", value="Livestream")

        else:
            embed.add_field(name="Duration", value=f'{seconds_to_timestring(voice_position)}/{seconds_to_timestring(total_seconds)}')

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Now_Playing(bot))
    