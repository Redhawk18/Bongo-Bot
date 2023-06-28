import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands

class autoplay(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="autoplay", description="Enables/Disables autoplaying from Youtube")
    async def autoplay(self, interaction: discord.Interaction):
        if autoplay := self.bot.cache[interaction.guild_id].autoplay:
            autoplay = True
            await interaction.response.send_message("**Autoplay** 😵‍💫 is enabled")

        else:
            autoplay = False
            await interaction.response.send_message("**Autoplay** 😵‍💫 is disabled")

async def setup(bot):
    await bot.add_cog(autoplay(bot))
