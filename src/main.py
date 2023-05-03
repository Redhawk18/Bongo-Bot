import asyncio
import os
from os import getenv
import logging
from pathlib import Path
import sys

import discord
from dotenv import load_dotenv

from bongo_bot import Bongo_Bot

#logging
discord.utils.setup_logging(level=logging.INFO)
log = logging.getLogger(__name__)

root_path = Path(__file__).parent.resolve().parent.resolve()
if len(sys.argv) < 2: #add everything to environ
    if not Path.is_file(root_path.joinpath(".env")):
        log.critical("you forgot the .env file")
        exit()

    load_dotenv(root_path.joinpath(".env"))

TOKEN = getenv('DISCORD_TOKEN')

bot = Bongo_Bot()

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
