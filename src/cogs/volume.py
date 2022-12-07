import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands, get_voice

class Volume(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="volume", description="Sets the volume of the player")
    @app_commands.describe(percent="Volume of the player")
    async def volume(self, interaction: discord.Interaction, percent: app_commands.Range[float, 0, 100]):
        voice = await get_voice(interaction)
        if voice is None or not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing):
            return

        if voice.is_connected():
            await voice.set_volume(percent)
            await interaction.response.send_message(f'**Volume** :loud_sound: changed to {percent}%')

        else:
            await interaction.response.send_message("Not connected to voice chat")

async def setup(bot):
    await bot.add_cog(Volume(bot))
