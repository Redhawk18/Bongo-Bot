import logging

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

import bongo_bot

log = logging.getLogger(__name__)


class Loop(commands.Cog):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @app_commands.command(
        name="loop", description="Loops the current song until disabled"
    )
    @app_commands.guild_only()
    async def loop(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction
        ) and not await self.bot.does_voice_exist(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)
        queue: wavelink.Queue = player.queue

        if wavelink.QueueMode.loop == queue.mode:
            queue.mode = wavelink.QueueMode.normal
            log.info(f"Disabled loop name: {player.guild.name}:{player.guild.id}")
            await interaction.response.send_message("**Loop Disabled** 🔁")

        else:
            queue.mode = wavelink.QueueMode.loop
            log.info(f"Enabled loop name: {player.guild.name}:{player.guild.id}")
            await interaction.response.send_message("**Loop Enabled** 🔁")


async def setup(bot):
    await bot.add_cog(Loop(bot))
