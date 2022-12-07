import discord
from discord import app_commands
from discord.ext import commands

class Queue_Clear(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="queue-clear", description="Clears everything in the queue")
    async def queue_clear(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].song_queue.clear()
        await interaction.response.send_message("**Cleared queue** :books:")

async def setup(bot):
    await bot.add_cog(Queue_Clear(bot))
