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
    async def roll(self, ctx, dienumber):
        try:
            int(dienumber)
        except ValueError:
            await ctx.send("Input invalid")
            return

        if dienumber < 1:
            await ctx.send("Input invalid")
            return


        await ctx.send(f'**Rolled** :game_die: {random.randint(1, dienumber)} of a {dienumber}-sided die')


def setup(client):
    client.add_cog(Util_Commands(client))
