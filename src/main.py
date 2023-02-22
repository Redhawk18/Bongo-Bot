import asyncio
from os import getenv
import logging
from pathlib import Path

import discord
from dotenv import load_dotenv

from bongo_bot import Bongo_Bot

root_path = Path(__file__).parent.resolve().parent.resolve()
env_path = root_path.joinpath(".env")

if not Path.is_file(env_path):
    print("you forgot the .env file")
    exit()

load_dotenv(env_path)
TOKEN = getenv('DISCORD_TOKEN')

bot = Bongo_Bot(env_path)

async def main():
    async with bot:
        #load cogs
        for file in root_path.glob('./src/cogs/*.py'):
            await bot.load_extension(f'cogs.{file.name[:-3]}')
        
        #start bot
        discord.utils.setup_logging(level=logging.INFO)
        await bot.start(TOKEN)

asyncio.run(main())
