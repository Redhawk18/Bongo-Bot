import random

import discord
from discord import app_commands
from discord.ext import commands

class Queue_Shuffle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="queue-shuffle", description="shuffles the queue")
    async def queue_shuffle(self, interaction: discord.Interaction):
        if len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) > 1:
            random.shuffle(self.bot.variables_for_guilds[interaction.guild_id].song_queue)
            await interaction.response.send_message("**Shuffled queue** :books:")

        else:
            await interaction.response.send_message("Nothing to shuffle")

async def setup(bot):
    await bot.add_cog(Queue_Shuffle(bot))
