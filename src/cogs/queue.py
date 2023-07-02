import random

import discord
from discord import app_commands
from discord.ext import commands


@app_commands.guild_only()
class Queue(commands.GroupCog, group_name="queue"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="list", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def list(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        if player.queue.is_empty: # TODO player can be none
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        queue = player.queue.copy()

        output = ""
        total_milliseconds = 0
        for i, track in enumerate(queue):
            if len(output) > 4000:  # limit for embed description is 4096 characters
                output += "\n"
                output += f'*{len(player.queue) - i} remaining songs not listed*'
                break

            output += f'{i +1}. `{track.title}` - '

            if track.is_stream: # Livestreams don't have length
                output += f'Livestream`\n'

            else:
                output += f'`{self.bot.milliseconds_to_timestring(track.length)}`\n'
                total_milliseconds += track.length

            print(track.length)

        embed = discord.Embed(
            title="**Queue** 📚",
            description=output,
            color=discord.Color.red(),
        )

        embed.set_footer(
            text=f"Total length: {self.bot.milliseconds_to_timestring(total_milliseconds)}"
        )

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="clear", description="Clears everything in the queue")
    async def clear(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        player.queue.clear()
        await interaction.response.send_message("**Cleared queue** 📚")

    @app_commands.command(
        name="remove",
        description="Removes a song from the queue based on its track number",
    )
    @app_commands.describe(queue_position="The position of the track to be removed")
    async def remove(self, interaction: discord.Interaction, queue_position: int):
        player: wavelink.player = await self.bot.get_player(interaction)

        if player.queue.is_empty:
            interaction.response.send_message("Queue is empty")
            return

        if player.queue.count < queue_position:
            interaction.response.send_message("Position too large")
            return

        del player.queue[queue_position]
        await interaction.response.send_message("**Removed track** 🚮")

    @app_commands.command(name="shuffle", description="shuffles the queue")
    async def queue_shuffle(self, interaction: discord.Interaction):
        player: wavelink.player = await self.bot.get_player(interaction)
        player.queue.shuffle()
        await interaction.response.send_message("**Shuffled queue** 📚")


async def setup(bot):
    await bot.add_cog(Queue(bot))
