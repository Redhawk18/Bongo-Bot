from math import ceil
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



def setup(client):
    client.add_cog(Util_Commands(client))
