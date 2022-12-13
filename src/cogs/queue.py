import discord
from discord import app_commands
from discord.ext import commands

from utilities import seconds_to_timedate

class Queue(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="queue", description="Lists the queue")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    async def queue(self, interaction: discord.Interaction):
        if len(self.bot.variables_for_guilds[interaction.guild_id].song_queue) == 0: #incase the queue was empty from the start
            await interaction.response.send_message("The queue is empty")
            return

        await interaction.response.send_message("Queue is loading")

        tempq = self.bot.variables_for_guilds[interaction.guild_id].song_queue.copy()

        #store every element in a string
        index = 0
        output = "Shows every song until the character limit is reached\n\n"
        total_seconds = 0
        while tempq:
            #get the url of the video
            track, _, _ = tempq.pop()

            if len(output) < 4050: #limit 4096
                output += (f'{index +1}. `{track.title}` - `{seconds_to_timedate(track.length)}`\n')

            total_seconds += track.length
            index += 1
        
        embed = discord.Embed(
            title = "**Queue** :books:",
            description = output,
            color = discord.Color.red(),
        )

        #figure the length of the queue
        embed.set_footer(text=f'Total length: {seconds_to_timedate(total_seconds)}')

        if self.bot.variables_for_guilds[interaction.guild_id].loop_enabled:
            embed.set_footer(text="Total length: Forever")

        await interaction.edit_original_response(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(Queue(bot))
