import discord
from discord import app_commands
from discord.ext import commands


class Force_Skip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="force-skip", description="Skips the track")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def force_skip(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if player is None or not await self.bot.able_to_use_commands(
            interaction,
            self.bot.cache[interaction.guild_id].music_channel_id,
            self.bot.cache[interaction.guild_id].music_role_id,
        ):
            return

        player = await self.bot.get_player(interaction)

        if player.is_playing():
            await player.stop()
            await interaction.response.send_message("**Skipped** ⏭")

        else:
            await interaction.response.send_message("Nothing is playing")


async def setup(bot):
    await bot.add_cog(Force_Skip(bot))
