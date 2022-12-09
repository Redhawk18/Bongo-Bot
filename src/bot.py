import asyncio
from collections import defaultdict
import logging
import os

import asyncpg
import discord
from discord.ext import commands
from dotenv import load_dotenv

import server_infomation

#.env
if not os.path.isfile('.env'):
    print("you forgot the .env file")
    exit()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Bongo_Bot(commands.Bot):
    """Handles intents and prefixs automatically"""
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix = "!", intents = self.get_intents(), *args, **kwargs)
        self.tree.on_error = self.on_tree_error

        self.variables_for_guilds = defaultdict(server_infomation.Server_Infomation) 

    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')

    async def setup_hook(self):
        #sync new commands
        #await bot.tree.sync()

        #create and setup database
        await self.create_database_pool()
        await self.load_data()

    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

    async def close(self):
        print("Database Shuting Down")
        await self.database.close()

        await super().close()

    def get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        return intents

    async def create_database_pool(self) -> None:
        self.database: asyncpg.Pool = await asyncpg.create_pool(
        database="Bongo", 
        user="postgres", 
        host="127.0.0.1", 
        port="5432", 
        password=os.getenv('DATABASE_PASSWORD')
        )
        print("Database connected")

    async def load_data(self) -> None:
        """Loads the entire table entry by entry into variables_for_guilds"""
        

        print("Database loaded into cache")

bot = Bongo_Bot()

async def main():
    async with bot:
        #load cogs
        for filename in os.listdir('./src/cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
        
        #start bot
        discord.utils.setup_logging(level=logging.INFO)
        await bot.start(TOKEN)

asyncio.run(main())
