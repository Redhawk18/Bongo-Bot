from math import ceil
import random

import discord
from discord.ext import commands

class Util_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    @commands.Cog.listener()
    async def on_ready(self):
        print("util commands lister online")


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** :ping_pong: {ceil(self.client.latency*1000)}ms')


    @commands.command()
    async def roll(self, ctx, max : int):
        if max < 1:
            await ctx.send("Input invalid")
            return


        await ctx.send(f'**Rolled** :game_die: {random.randint(1, max)} of a {max}-sided die')

    @commands.command()
    async def multipleroll(self, ctx, max : int, number_of_rolls : int):
        if number_of_rolls < 1 or max < 1:
            await ctx.send("Input invalid")
            return

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
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Util_Commands(client))
