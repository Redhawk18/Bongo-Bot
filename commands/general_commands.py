from http import client
import discord
from discord.ext import commands

class General_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print("general commands lister online")

    #commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! :ping_pong:')

def setup(client):
    client.add_cog(General_Commands(client))
