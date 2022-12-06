import asyncio
from collections import defaultdict
import logging
import os

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

#intents





class Bongo_Bot(commands.Bot):
    """Handles intents and prefixs automatically"""
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix = "!", intents = self.get_intents(), *args, **kwargs)
        self.tree.on_error = self.on_tree_error

    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')

        #sync new commands
        await bot.tree.sync()

    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

    def get_intents(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        return intents

bot = Bongo_Bot()


async def main():
    async with bot:
        #add dynamic attribute
        bot.variables_for_guilds = defaultdict(server_infomation.Server_Infomation) 

        #load cogs
        for filename in os.listdir('./src/commands'):
            if filename.endswith('.py'):
                await bot.load_extension(f'commands.{filename[:-3]}')
        
        #start bot
        discord.utils.setup_logging(level=logging.INFO)
        await bot.start(TOKEN)


asyncio.run(main())
