import random

import discord
from discord import app_commands
from discord.ext import commands

from utilities import seconds_to_timestring


@app_commands.guild_only()
class Queue(commands.GroupCog, group_name="queue"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="list", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def list(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        if player.queue.empty():
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        temp_queue = player.queue.copy()

        # store every element in a string
        index = 0
        output = ""
        total_seconds = 0
        while temp_queue:
            # get the url of the video
            track = temp_queue.pop()

            if len(output) < 4000:  # limit for embed description is 4096 characters
                if track.is_stream:
                    output += f'{index +1}. `{track.title}` - `Livestream`\n'
                    
                else:
                    output += f"{index +1}. `{track.title}` - `{self.bot.seconds_to_timestring(track.length)}`\n"
                index += 1

            if not track.is_stream:
                total_seconds += track.length / 1000

        output += "\n"
        output += f'*{len(self.bot.cache[interaction.guild_id].song_queue) - index} remaining songs not listed...*'

        embed = discord.Embed(
            title="**Queue** 📚",
            description=output,
            color=discord.Color.red(),
        )

        # figure the length of the queue
        embed.set_footer(text=f"Total length: {self.bot.seconds_to_timestring(total_seconds)}")

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="clear", description="Clears everything in the queue")
    async def clear(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        player.queue.clear()
        await interaction.response.send_message("**Cleared** 📚 queue")

    @app_commands.command(
        name="remove",
        description="Removes a song from the queue based on its track number",
    )
    @app_commands.describe(queue_position="The position of the track to be removed")
    async def remove(self, interaction: discord.Interaction, queue_position: int):
        player: wavelink.player = await self.bot.get_player(interaction)

        if player.queue.is_empty():
            interaction.response.send_message("Queue is empty")
            return

        if player.queue.count < queue_position:
            interaction.response.send_message("Position too large") 
            return

        del player.queue[queue_position]
        interaction.response.send_message("**Removed** 🚮 track")


    @app_commands.command(name="shuffle", description="shuffles the queue")
    async def queue_shuffle(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        player.queue.shuffle()
        await interaction.response.send_message("**Shuffled queue** 📚")


async def setup(bot):
    await bot.add_cog(Queue(bot))
