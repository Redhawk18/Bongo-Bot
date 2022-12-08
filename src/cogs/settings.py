import discord
from discord import app_commands
from discord.ext import commands

@commands.has_permissions(administrator=True)
class Settings(commands.GroupCog, group_name='settings'):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass
    
    @app_commands.command(name="list", description="Lists all settings")
    async def settings_list(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = "**Settings** :gear:",
            description = "Use the set commands to set values",
            color = discord.Color.red()
        )
        embed.add_field(name="Music Channel", value=self.bot.get_channel(self.bot.variables_for_guilds[interaction.guild_id].music_channel_id).mention)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set-music-channel", description="Sets the current text channel as the only one music commands can be run from")
    async def settings_set_music_channel(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].music_channel_id = interaction.channel_id

        await interaction.response.send_message(f'Set music channel to {interaction.channel.mention}')

async def setup(bot):
    await bot.add_cog(Settings(bot))