import discord
from discord import app_commands
from discord.ext import commands

class Queue_Remove(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="queue-remove", description="Removes a song from the queue based on its track number")
    @app_commands.describe(queue_position="The position of the track to be removed")
    async def queue_remove(self, interaction: discord.Interaction, queue_position : int):
        if queue_position > len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) or queue_position < 0:
            await interaction.response.send_message("Input invalid")
            return

        #because of how the remove function works we have to make a copy
        tempq = self.bot.variables_for_guilds[interaction.guild_id].song_queue.copy()

        for _ in range(queue_position -1): #so we dont have to save what's popped
            tempq.pop()

        #we should have the url of the track we want to remove
        self.bot.variables_for_guilds[interaction.guild_id].song_queue.remove(tempq.pop())
        await interaction.response.send_message("**Removed from queue** :books:")

async def setup(bot):
    await bot.add_cog(Queue_Remove(bot))
