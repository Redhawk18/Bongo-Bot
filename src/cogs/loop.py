import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands

class Loop(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="loop", description="Loops the current song until disabled")
    async def loop(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing):
            return

        if not self.bot.variables_for_guilds[interaction.guild_id].is_playing:
            await interaction.response.send_message("Nothing Playing")
            return

        if self.bot.variables_for_guilds[interaction.guild_id].loop_enabled: #disable loop
            track, _, _ = self.bot.variables_for_guilds[interaction.guild_id].song_queue.pop()
            self.bot.variables_for_guilds[interaction.guild_id].loop_enabled = False
            await interaction.response.send_message("**Loop Disabled** :repeat:")

        else: #enable loop
            #add current song to the top of the queue once
            track = self.bot.variables_for_guilds[interaction.guild_id].now_playing_track
            self.bot.variables_for_guilds[interaction.guild_id].song_queue.append((track, interaction, None))
            self.bot.variables_for_guilds[interaction.guild_id].loop_enabled = True
            await interaction.response.send_message("**Loop Enabled** :repeat:")

async def setup(bot):
    await bot.add_cog(Loop(bot))
    