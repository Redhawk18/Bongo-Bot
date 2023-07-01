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
        player = await self.bot.get_player(interaction)
        if not await self.bot.able_to_use_commands(
            interaction,
            self.bot.cache[interaction.guild_id].music_channel_id,
            self.bot.cache[interaction.guild_id].music_role_id,
        ):
            return

        if not player.is_paused():
            await player.pause()
            await interaction.response.send_message("**Paused** ⏸")
            # playing_view = self.bot.cache[interaction.guild_id].playing_view
            # await playing_view.edit_view(interaction, False)

        else:
            await interaction.response.send_message("Already paused")


async def setup(bot):
    await bot.add_cog(Pause(bot))
