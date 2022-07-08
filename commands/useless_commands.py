import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

class Useless_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    #events
    @commands.Cog.listener()
    async def on_ready(self):
        print("useless commands lister online")


    @app_commands.command()
    async def frank(self, interaction: discord.Interaction):
        await interaction.response.send_message('https://tenor.com/view/gezer123123123-gif-18858197')


    @commands.Cog.listener()
    async def on_message(self, message):
        #get trolled user from env
        load_dotenv()
        TROLLED_USER = os.getenv('TROLLED_USER')

        if message.author.name + "#" + message.author.discriminator != TROLLED_USER:
            return

        if message.content.startswith('!'):
            return

        #1 in 20 messages
        if random.randint(1, 20) == 20:
            await message.add_reaction("🐧")



async def setup(client):
    await client.add_cog(Useless_Commands(client))
