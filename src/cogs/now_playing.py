import discord
from discord import app_commands
from discord.ext import commands


class Now_Playing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="now-playing", description="Show the playing song")
    @app_commands.guild_only()
    async def now_playing(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        
        if not player.current:
            await interaction.response.send_message("Nothing is playing")
            return

        embed = discord.Embed(
            title="**Now Playing** 🎶",
            url=player.current.uri,
            color=discord.Color.red(),
            description="",
        )
        embed.set_thumbnail(url=player.current.thumbnail)
        embed.add_field(name="Title", value=player.current.title, inline=False)
        embed.add_field(name="Uploader", value=player.current.author)

        total_seconds = player.current.length / 1000
        voice_position = (
            await self.bot.get_player(interaction.guild_id, interaction)
        ).position / 1000

        if player.current.is_stream:
            embed.add_field(name="Duration", value="Livestream")

        else:
            embed.add_field(
                name="Duration",
                value=f"{self.bot.seconds_to_timestring(voice_position)}/{self.bot.seconds_to_timestring(total_seconds)}",
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Now_Playing(bot))
