import random

import discord
from discord import app_commands
from discord.ext import commands

class Roll(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="roll", description="Rolls a sided die, however many times")
    @app_commands.describe(die_sides="How many sides the die has", rolls="How many times the die is rolled")
    @app_commands.guild_only()
    async def roll(self, interaction: discord.Interaction, die_sides: app_commands.Range[int, 2], rolls: app_commands.Range[int, 1, 24]=1):
        sum = 0
        output = f'A {die_sides}-sided die was rolled {rolls} times\n'
        for _ in range(rolls):
            current_roll = random.randint(1, die_sides)
            sum += current_roll
            output += f'Rolled {current_roll} :game_die:\n'

        #sum print
        output += "\n"
        output += f'The sum is **{sum} of {rolls * die_sides}**'

        embed = discord.Embed(
            title = "**Roll** :game_die:",
            description = output,
            color = discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Roll(bot))