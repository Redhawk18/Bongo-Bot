import discord
from discord import app_commands
from discord.ext import commands


class Loop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="loop", description="Loops the current song until disabled"
    )
    @app_commands.guild_only()
    async def loop(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(  # TODO do some testng to see if this can be put in the command method instead of the helper method
            interaction,
            self.bot.cache[interaction.guild_id].music_channel_id,
            self.bot.cache[interaction.guild_id].music_role_id,
        ):
            return

        player: wavelink.player = await self.bot.get_player(interaction)

        if player.queue.loop:
            player.queue.loop = False
            await interaction.response.send_message("**Loop Disabled** 🔁")

        else:
            player.queue.loop = True
            await interaction.response.send_message("**Loop Enabled** 🔁")


async def setup(bot):
    await bot.add_cog(Loop(bot))
