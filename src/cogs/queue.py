import discord
from discord import app_commands
from discord.ext import commands
import wavelink

import bongo_bot


@app_commands.guild_only()
class Queue(commands.GroupCog, group_name="queue"):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Clears everything in the queue")
    async def clear(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)

        player.queue.clear()
        await interaction.response.send_message("**Cleared queue** 📚")

    @app_commands.command(name="list", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def list(self, interaction: discord.Interaction):
        player: wavelink.Player = await self.bot.get_player(interaction)

        if player.queue.is_empty or player is None:
            await interaction.response.send_message("The queue is empty")
            return

        output = ""
        total_milliseconds = 0
        for i, track in enumerate(player.queue):
            if len(output) > 4000:  # limit for embed description is 4096 characters
                output += "\n"
                output += f"*{len(player.queue) - i} remaining songs not listed*"
                break

            output += f"{i +1}. `{track.title}` - "

            if track.is_stream:  # Livestreams don't have length
                output += f"Livestream`\n"

            else:
                output += f"`{self.bot.milliseconds_to_timestring(track.length)}`\n"
                total_milliseconds += track.length

        embed = discord.Embed(
            title="**Queue** 📚",
            description=output,
            color=discord.Color.red(),
        )

        embed.set_footer(
            text=f"Total length: {self.bot.milliseconds_to_timestring(total_milliseconds)}"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="remove",
        description="Removes a song from the queue",
    )
    @app_commands.describe(track_number="The position of the track to be removed")
    async def remove(
        self,
        interaction: discord.Interaction,
        track_number: app_commands.Range[int, 1],
    ):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)

        if not player.queue:
            await interaction.response.send_message("Queue is empty")
            return

        if len(player.queue) < track_number:
            await interaction.response.send_message(
                "Track number is larger than queue size"
            )
            return

        player.queue.delete(track_number - 1)
        await interaction.response.send_message("**Removed track** 🚮")

    @app_commands.command(name="shuffle", description="shuffles the queue")
    async def shuffle(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)
        player.queue.shuffle()
        await interaction.response.send_message("**Shuffled queue** 📚")


async def setup(bot):
    await bot.add_cog(Queue(bot))
