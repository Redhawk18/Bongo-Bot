import random

import discord
from discord import app_commands
from discord.ext import commands

from utilities import seconds_to_timedate

@app_commands.guild_only()
class Queue(commands.GroupCog, group_name='queue'):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass
    
    @app_commands.command(name="list", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def queue_list(self, interaction: discord.Interaction):
        if len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) == 0: #incase the queue was empty from the start
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        tempq = self.bot.variables_for_guilds[interaction.guild_id].song_queue.copy()

        #store every element in a string
        index = 0
        output = "Shows every song until the character limit is reached\n\n"
        total_seconds = 0
        while tempq:
            #get the url of the video
            track, _, _ = tempq.pop()

            if len(output) < 4050: #limit 4096
                output += (f'{index +1}. `{track.title}` - `{seconds_to_timedate(track.length)}`\n')

            total_seconds += track.length
            index += 1
        
        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )

        #figure the length of the queue
        embed.set_footer(text=f'Total length: {seconds_to_timedate(total_seconds)}')

        if self.bot.variables_for_guilds[interaction.guild_id].loop_enabled:
            embed.set_footer(text="Total length: Forever")

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="clear", description="Clears everything in the queue")
    async def queue_clear(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].song_queue.clear()
        await interaction.response.send_message("**Cleared queue** :books:")

    @app_commands.command(name="remove", description="Removes a song from the queue based on its track number")
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

    @app_commands.command(name="shuffle", description="shuffles the queue")
    async def queue_shuffle(self, interaction: discord.Interaction):
        if len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) > 1:
            random.shuffle(self.bot.variables_for_guilds[interaction.guild_id].song_queue)
            await interaction.response.send_message("**Shuffled queue** :books:")

        else:
            await interaction.response.send_message("Nothing to shuffle")

async def setup(bot):
    await bot.add_cog(Queue(bot))