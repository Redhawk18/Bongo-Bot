from math import ceil
import random

import discord
from discord import app_commands
from discord.ext import commands

class Util_Commands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_ready(self):
        print("util commands lister online")
        

    @app_commands.command(name='ping', description='Pong!')
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**Pong!** :ping_pong: {ceil(self.client.latency*1000)}ms')


    @app_commands.command(name='roll', description='Rolls a n-sided die')
    async def roll(self, interaction: discord.Interaction, max: app_commands.Range[int, 2]):
        await interaction.response.send_message(f'**Rolled** :game_die: {random.randint(1, max)} of a {max}-sided die')


    @app_commands.command(name='multiple-roll', description='Rolls a n-sided die x number of times')
    async def multipleroll(self, interaction: discord.Interaction, max: app_commands.Range[int, 2], number_of_rolls: app_commands.Range[int, 1, 192]):
        sum = 0
        output = f'A {max}-sided die was rolled {number_of_rolls} times\n'
        for i in range(number_of_rolls):
            current_roll = random.randint(1, max)
            sum += current_roll
            output += f'Rolled {current_roll} :game_die:\n'

        #sum print
        output += "\n"
        output += f'The sum is **{sum} of {number_of_rolls * max}**'

        embed = discord.Embed(
            title = "**Multiple Rolled** :game_die:",
            description = output,
            color = discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)



async def setup(client):
    await client.add_cog(Util_Commands(client))