from math import ceil

import discord
from discord import app_commands
from discord.ext import commands


class Skip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="skip", description="Calls a vote to skip the track")
    @app_commands.guild_only()
    async def skip(self, interaction: discord.Interaction):
        if not self.bot.does_voice_exist(interaction):
            await interaction.response.send_message("Nothing is playing")
            return

        
        player = await self.bot.get_player(interaction)


        if not player.is_playing():
            await interaction.response.send_message("Nothing is playing")
            return

        # check list if the user is the same
        user_who_want_to_skip = self.bot.cache[
            interaction.guild_id
        ].user_who_want_to_skip
        for id in user_who_want_to_skip:
            if id == interaction.user.id:  # already voted
                await interaction.response.send_message("You already voted")
                return

        # add user id to list
        user_who_want_to_skip.append(interaction.user.id)

        # check if its passed threshold
        voice_channel = interaction.user.voice.channel
        threshold = ceil((len(voice_channel.members) - 1) / 2)  # -1 for the bot itself

        if len(user_who_want_to_skip) >= threshold:  # enough people
            await self.bot.get_cog("Force_Skip").helper(interaction)

        else:  # not enough people
            await interaction.response.send_message(
                f"**Skipping? ({len(user_who_want_to_skip)}/{threshold} votes needed) or use `force-skip`**"
            )


async def setup(bot):
    await bot.add_cog(Skip(bot))
