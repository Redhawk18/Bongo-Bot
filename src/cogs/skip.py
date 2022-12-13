from math import ceil

import discord
from discord import app_commands
from discord.ext import commands

from utilities import able_to_use_commands, get_voice

class Skip(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="skip", description="Calls a vote to skip the track")
    async def skip(self, interaction: discord.Interaction):
        await self.helper(interaction)

    async def helper(self, interaction: discord.Interaction):
        voice = await get_voice(interaction)
        if voice is None or not await able_to_use_commands(interaction, self.bot.variables_for_guilds[interaction.guild_id].is_playing, self.bot.variables_for_guilds[interaction.guild_id].music_channel_id, self.bot.variables_for_guilds[interaction.guild_id].music_role_id):
            return

        if voice.is_playing():
            #check list if the user is the same
            for id in self.bot.variables_for_guilds[interaction.guild_id].user_who_want_to_skip:
                if id == interaction.user.id: #already voted
                    await interaction.response.send_message("You already voted")
                    return

            #add user id to list
            self.bot.variables_for_guilds[interaction.guild_id].user_who_want_to_skip.append(interaction.user.id)

            #check if its passed threshold
            voice_channel = interaction.user.voice.channel
            threshold = ceil((len(voice_channel.members)-1)/2) #-1 for the bot

            if len(self.bot.variables_for_guilds[interaction.guild_id].user_who_want_to_skip) >= threshold: #enough people
                await self.bot.get_cog("Force_Skip").helper(interaction)

            else: #not enough people
                await interaction.response.send_message(f'**Skipping? ({len(self.user_who_want_to_skip)}/{threshold} votes needed) or use `forceskip`**')

        else:
            await interaction.response.send_message("Nothing is playing")
            return

async def setup(bot):
    await bot.add_cog(Skip(bot))
