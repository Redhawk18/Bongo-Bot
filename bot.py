import asyncio
import logging
import os

import wavelink
import discord
from discord.ext import commands
from dotenv import load_dotenv

#.env
if not os.path.isfile('.env'):
    print("you forgot the .env file")
    exit()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#intents
bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.voice_states = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot = commands.Bot(command_prefix='!', intents=bot_intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    #sync new commands
    await bot.tree.sync()


async def main():
    async with bot:
        #load cogs
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                await bot.load_extension(f'commands.{filename[:-3]}')
        
        #start bot
        logging.basicConfig(level=logging.INFO)
        await bot.start(TOKEN)
        
    
    

asyncio.run(main())
