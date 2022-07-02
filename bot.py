import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!', case_insensitive=True, intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await client.load_extension(f'commands.{filename[:-3]}')

client.run(TOKEN)