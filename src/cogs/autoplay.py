import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands

class autoplay(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="autoplay", description="Enables/Disables autoplaying from Youtube")
    @app_commands.choices(choices=[
        app_commands.Choice(name="True", value=True),
        app_commands.Choice(name="False", value=False),
    ])
    async def frank(self, interaction: discord.Interaction, choice: app_commands.Choice[bool]):
        self.bot.cache[interaction.guild_id].autoplay = choice
        interaction.response.send_message(f'Autoplay is now {choice}')

async def setup(bot):
    await bot.add_cog(autoplay(bot))
