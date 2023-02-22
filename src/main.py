import asyncio
from os import getenv
import logging
from pathlib import Path

import discord
from dotenv import load_dotenv

from bongo_bot import Bongo_Bot

root_path = Path(__file__).parent.resolve().parent.resolve()

if not Path.is_file(root_path.joinpath(".env")):
    print("you forgot the .env file")
    exit()

load_dotenv(root_path.joinpath(".env"))
TOKEN = getenv('DISCORD_TOKEN')

bot = Bongo_Bot()

async def main():
    async with bot:
        #load cogs
        for file in root_path.glob('./src/cogs/*.py'):
            await bot.load_extension(f'cogs.{file.name[:-3]}')
        
        #start bot
        discord.utils.setup_logging(level=logging.INFO)
        await bot.start(TOKEN)

asyncio.run(main())
