import discord
from discord import app_commands
from discord.ext import commands

from utilities import get_voice

@app_commands.default_permissions(administrator=True)
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

        music_channel_id = self.bot.variables_for_guilds[interaction.guild_id].music_channel_id

        if music_channel_id is not None:
            embed.add_field(name="Music Channel", value=self.bot.get_channel(music_channel_id).mention)

        else:
            embed.add_field(name="Music Channel", value="None")

        music_role_id = self.bot.variables_for_guilds[interaction.guild_id].music_role_id
        if music_role_id is not None:
            embed.add_field(name="Music Role", value=self.bot.get_guild(interaction.guild_id).get_role(music_role_id).mention)

        else:
            embed.add_field(name="Music Role", value="None")

        embed.add_field(name="Volume :loud_sound:", value=self.bot.variables_for_guilds[interaction.guild_id].volume)

        await interaction.response.send_message(embed=embed)

    #TODO add cooldowns to all set and reset commands, because they will have to contact a database
    @app_commands.command(name="set-music-channel", description="Sets the current text channel as the only one music commands can be run from")
    async def settings_set_music_channel(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].music_channel_id = interaction.channel_id

        await interaction.response.send_message(f'Set music channel to {interaction.channel.mention}')
        await self.update_database_value()

    @app_commands.command(name="reset-music-channel", description="Resets the music channel, so any channel can use music commands")
    async def settings_reset_music_channel(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].music_channel_id = None

        await interaction.response.send_message(f'Music channel reset')
        await self.update_database_value()

    @app_commands.command(name="set-music-roleee", description="Sets a role users are required to have to use music commands")
    @app_commands.describe(role="The only role that can use music commands")
    async def settings_set_music_role(self, interaction: discord.Interaction, role: discord.Role):
        self.bot.variables_for_guilds[interaction.guild_id].music_role_id = role.id

        await interaction.response.send_message(f'Set music role to {self.bot.get_guild(interaction.guild_id).get_role(role.id).mention}')
        await self.update_database_value()

    @app_commands.command(name="reset-music-role", description="Reset the role required to play music commands")
    async def settings_reset_music_role(self, interaction: discord.Interaction):
        self.bot.variables_for_guilds[interaction.guild_id].music_role_id = None

        await interaction.response.send_message(f'Music role reset')
        await self.update_database_value()

    @app_commands.command(name="volume", description="Sets the volume of the player")
    @app_commands.describe(volume="Volume of the player")
    async def volume(self, interaction: discord.Interaction, volume: app_commands.Range[int, 0, 100]):
        voice = await get_voice(interaction, False)
        if voice is None:
            await voice.set_volume(volume)

        self.bot.variables_for_guilds[interaction.guild_id].volume = volume
        await interaction.response.send_message(f'**Volume** :loud_sound: changed to {volume}%')
        await self.update_database_value()

    async def update_database_value():
        print("TODO update_database_value")

async def setup(bot):
    await bot.add_cog(Settings(bot))