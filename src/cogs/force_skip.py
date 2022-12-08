import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands, get_voice

class Force_Skip(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="force-skip", description="Skips the track")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.guild_id, i.user.id))
    async def force_skip(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        voice = await get_voice(interaction)
        if voice is None or not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing, self.bot.variables_for_guilds[interaction.guild_id].music_channel_id):
            return

        if voice.is_playing():
            await voice.stop()
            await interaction.response.send_message("**Skipped** :track_next:")

        else:
            await interaction.response.send_message("Nothing is playing")

async def setup(bot):
    await bot.add_cog(Force_Skip(bot))
    