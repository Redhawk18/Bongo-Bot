import logging

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

import bongo_bot

log = logging.getLogger(__name__)


class Disconnect(commands.Cog):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(interaction):
            return

        player: wavelink.Player = await self.bot.get_player(interaction)

        if player.connected():
            await self.stop_voice(player)
            await interaction.response.send_message("**Disconnected** 🎸")

        else:
            await interaction.response.send_message("Already disconnected")

    async def stop_voice(self, voice: discord.VoiceClient):
        log.info(f"Disconnecting in name: {voice.guild.name}, id: {voice.guild.id}")
        await self.bot.edit_view_message(voice.guild.id, None)
        await voice.disconnect()


async def setup(bot):
    await bot.add_cog(Disconnect(bot))
