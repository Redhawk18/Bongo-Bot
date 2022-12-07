from math import floor

import discord
from discord import app_commands
from discord.ext import commands

from utilities import add_zero

class Queue(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="queue", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        if len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) == 0: #incase the queue was empty from the start
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        tempq = self.bot.variables_for_guilds[interaction.guild_id].song_queue.copy()

        #store every element in a string
        index = 0
        output = ""
        total_seconds = 0
        while tempq:
            #get the url of the video
            track, _, _ = tempq.pop()

            minutes, seconds = divmod(track.length, 60)
            if minutes >= 60:
                hours, minutes = divmod(minutes, 60)
                output += (f"{index +1}. `{track.title}` - `{floor(hours)}:{add_zero(floor(minutes))}:{add_zero(floor(seconds))}`\n")
            else:
                output += (f"{index +1}. `{track.title}` - `{floor(minutes)}:{add_zero(floor(seconds))}`\n")

            total_seconds += track.length
            index += 1
            if index > 50: #giant queues have trouble loading
                break

        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )

        #figure the length of the queue
        queue_minutes, queue_seconds = divmod(total_seconds, 60)
        if queue_minutes >= 60:
            queue_hours, queue_minutes = divmod(queue_minutes, 60)
            embed.set_footer(text=f'Total length: {floor(queue_hours)}:{add_zero(floor(queue_minutes))}:{add_zero(floor(queue_seconds))}')
        else:
            embed.set_footer(text=f'Total length: {floor((queue_minutes))}:{add_zero(floor(queue_seconds))}')

        if self.bot.variables_for_guilds[interaction.guild_id].loop_enabled:
            embed.set_footer(text="Total length: Forever")

        await interaction.edit_original_response(content="", embed=embed)

async def setup(bot):
    await bot.add_cog(Queue(bot))
