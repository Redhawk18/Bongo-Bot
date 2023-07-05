import discord
from discord import app_commands
from discord.ext import commands


class Pause(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pause", description="Pauses track")
    @app_commands.guild_only()
    async def pause(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player = await self.bot.get_player(interaction)

        if not player.is_paused():
            await player.pause()
            await interaction.response.send_message("**Paused** ⏸")
            await player.view.edit_view(interaction, False)

        else:
            await interaction.response.send_message("Already paused")


async def setup(bot):
    await bot.add_cog(Pause(bot))
