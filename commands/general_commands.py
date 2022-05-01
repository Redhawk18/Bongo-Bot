import random

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

    @commands.command()
    async def quote(self, ctx):
        epic_quotes = [
        'Mimosa is literally orihime',
        'Hi Ben jojolion isnt coming out till the 19th, feelsbadman\n Wait part 6 ended this month?\n part 6 ended in 2005',
        'hi guys\n Why\n https://tenor.com/view/xqc-arabfunny-arabic-saudi-arabia-projared-gif-18306091',
        'https://tenor.com/view/gezer123123123-gif-18858197',
        'https://tenor.com/view/stop-hitting-my-child-in-gif-25029977'
        ]    
        response = random.choice(epic_quotes)
        await ctx.send(response)

    @commands.command()
    async def frank(self, ctx):
        await ctx.send('https://tenor.com/view/gezer123123123-gif-18858197')



def setup(client):
    client.add_cog(General_Commands(client))
