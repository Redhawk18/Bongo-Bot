import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands


class Disconnect(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    @app_commands.guild_only()
    async def disconnect(self, interaction: discord.Interaction):
        player = await self.bot.get_player(interaction.guild_id, interaction)
        if player is None or not await able_to_use_commands(
            interaction,
            self.bot.cache[interaction.guild_id].music_channel_id,
            self.bot.cache[interaction.guild_id].music_role_id,
        ):
            return

        if player.is_connected():
            await self.stop_voice_functions(player)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** 🎸")

        else:
            await interaction.response.send_message("Already disconnected")

    async def stop_voice_functions(self, voice: discord.VoiceClient):
        await voice.stop()
        await voice.disconnect()


async def setup(bot):
    await bot.add_cog(Disconnect(bot))
