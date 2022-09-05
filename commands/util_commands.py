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
        

    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**Pong!** :ping_pong: {ceil(self.client.latency*1000)}ms')


    @app_commands.command(name="roll", description="Rolls a n-sided die")
    async def roll(self, interaction: discord.Interaction, max: app_commands.Range[int, 2]):
        await interaction.response.send_message(f'**Rolled** :game_die: {random.randint(1, max)} of a {max}-sided die')


    @app_commands.command(name="multiple-roll", description="Rolls a n-sided die x number of times")
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


    @app_commands.command(name="poll", description='creates a poll with emotes to vote by')
    async def poll(self, interaction: discord.Interaction, title: str, option1: str, option2: str, option3: str=None, option4: str=None, option5: str=None, option6: str=None ,option7: str=None, option8: str=None, option9: str=None, option10: str=None):
        #take every option and put it in a list to loop through
        options = []
        num_to_word = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")

        #required args
        options.append(option1)
        options.append(option2)

        #this is truly spaghetti code
        if option3 is not None:
            options.append(option3)
        if option4 is not None:
            options.append(option4)
        if option5 is not None:
            options.append(option5)
        if option6 is not None:
            options.append(option6)
        if option7 is not None:
            options.append(option7)
        if option8 is not None:
            options.append(option8)
        if option9 is not None:
            options.append(option9)
        if option10 is not None:
            options.append(option10)

        #loop through valid options and create a string for embed
        description = ""
        index = 0
        for item in options:
            description += num_to_word[index] + " : " + item + "\n\n"
            index += 1

        #create embed with those options left
        embed = discord.Embed(
            title = title,
            description = description,
            color = discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)

        #add reactions for each valid option left
        message = await interaction.original_response()
        for index in range(len(options)):
            await message.add_reaction(num_to_word[index])

        

async def setup(client):
    await client.add_cog(Util_Commands(client))