from collections import defaultdict
from os import getenv

import asyncpg
import discord
from discord.ext import commands

from dotenv import load_dotenv

import server_infomation

class Bongo_Bot(commands.Bot):
    """Handles intents, prefixs, and database init automatically"""
    def __init__(self, env_path, *args, **kwargs):
        super().__init__(command_prefix = "!", intents = self.get_intents(), *args, **kwargs)
        self.tree.on_error = self.on_tree_error

        self.dotenv_path = env_path
        self.variables_for_guilds = defaultdict(server_infomation.Server_Infomation) 

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        #sync new commands
        await self.tree.sync()

    async def setup_hook(self):
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
        database=getenv('DATABASE_DATABASE'),
        user=getenv('DATABASE_USER'),
        host=getenv('DATABASE_HOST'),
        port=getenv('DATABASE_PORT'),
        password=getenv('DATABASE_PASSWORD')
        )
        print("Database connected")

    async def load_data(self) -> None:
        """Loads the entire table entry by entry into variables_for_guilds"""
        records = await self.database.fetch('SELECT * FROM guilds')

        for record in records:
            self.variables_for_guilds[record['guild_id']].music_channel_id = record['music_channel_id']
            self.variables_for_guilds[record['guild_id']].music_role_id = record['music_role_id']
            self.variables_for_guilds[record['guild_id']].volume = record['volume']

        print("Database loaded into cache")