import logging

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger(__name__)


class Disconnect(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        if not await self.bot.able_to_use_commands(
            interaction,
            self.bot.cache[interaction.guild_id].music_channel_id,
            self.bot.cache[interaction.guild_id].music_role_id,
        ):
            return

        player = await self.bot.get_player(interaction)

        if player.is_connected():
            await self.stop_voice_functions(player)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** 🎸")

        else:
            await interaction.response.send_message("Already disconnected")

    async def stop_voice_functions(self, voice: discord.VoiceClient):
        await voice.stop()
        await voice.disconnect()
        log.info(f"Disconnecting in name: {voice.guild.name}, id: {voice.guild.id}")


async def setup(bot):
    await bot.add_cog(Disconnect(bot))
