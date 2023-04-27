import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands, get_voice

class Resume(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="resume", description="Resumes track")
    @app_commands.guild_only()
    async def resume(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        voice = await get_voice(interaction)
        if voice is None or not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing, self.bot.variables_for_guilds[interaction.guild_id].music_channel_id, self.bot.variables_for_guilds[interaction.guild_id].music_role_id):
            return

        if voice.is_paused():
            await voice.resume()
            await interaction.response.send_message("**Resumed** ▶")
            playing_view = self.bot.variables_for_guilds[interaction.guild_id].playing_view
            await playing_view.edit_view(interaction, True)


        else:
            await interaction.response.send_message("Already resumed")

async def setup(bot):
    await bot.add_cog(Resume(bot))
