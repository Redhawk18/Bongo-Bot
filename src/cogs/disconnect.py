import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands, get_voice

class Disconnect(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="disconnect", description="disconnect from voice chat")
    async def disconnect(self, interaction: discord.Interaction):
        voice = await get_voice(interaction)
        if voice is None or not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing):
            return

        if voice.is_connected():
            await self.stop_voice_functions(voice)
            if not interaction.response.is_done():
                await interaction.response.send_message("**Disconnected** :guitar:")

        else:
            await interaction.response.send_message("Already disconnected")

    async def stop_voice_functions(self, voice: discord.VoiceClient):
        self.bot.variables_for_guilds[voice.guild.id].song_queue.clear() #wipe all future songs
        self.bot.variables_for_guilds[voice.guild.id].is_playing = False
        self.bot.variables_for_guilds[voice.guild.id].loop_enabled = False

        await voice.stop()
        await voice.disconnect()

async def setup(bot):
    await bot.add_cog(Disconnect(bot))
    