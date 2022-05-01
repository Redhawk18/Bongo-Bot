import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
#print(os.getenv('DISCORD_TOKEN'))
TOKEN = os.getenv('DISCORD_TOKEN')
TROLLED = os.getenv('TROLLED_USER')

#client = discord.Client()
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! :ping_pong: {round(client.latency * 1000)}ms')


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        client.load_extension(f'commands.{filename[:-3]}')


client.run(TOKEN)