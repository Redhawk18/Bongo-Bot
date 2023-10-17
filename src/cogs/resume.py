import discord
from discord import app_commands
from discord.ext import commands
import wavelink


class Resume(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="resume", description="Resumes track")
    @app_commands.guild_only()
    async def resume(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)

        if player.paused:
            await player.pause(False)
            await interaction.response.send_message("**Resumed** ▶")
            await player.view.edit_view(interaction, True)

        else:
            await interaction.response.send_message("Already resumed")


async def setup(bot):
    await bot.add_cog(Resume(bot))
