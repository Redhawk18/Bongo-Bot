from math import ceil
import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

class Frank(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name="frank", description="To be Frank")
    async def frank(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://tenor.com/view/gezer123123123-gif-18858197")
        
    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**Pong!** :ping_pong: {ceil(self.bot.latency*1000)}ms')

    @commands.Cog.listener()
    async def on_message(self, message):
        load_dotenv(self.bot.dotenv_path)
        TROLLED_USER_ID = int(os.getenv('TROLLED_USER_ID'))

        if TROLLED_USER_ID == message.author.id:
            if random.randint(1, 50) == 1:
                await message.add_reaction("🐧")

async def setup(bot):
    await bot.add_cog(Frank(bot))