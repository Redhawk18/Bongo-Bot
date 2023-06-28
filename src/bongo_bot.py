from collections import defaultdict
import logging
from os import getenv
from pathlib import Path
import sys

import asyncpg
import discord
from discord.ext import commands
import wavelink

from cache import Cache

log = logging.getLogger(__name__)

class Bongo_Bot(commands.Bot):
    """Handles intents, prefixs, and database init automatically"""
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix = "!", intents = self.get_intents(), *args, **kwargs)
        self.tree.on_error = self.on_tree_error

        self.cache = defaultdict(Cache)
        
    async def on_ready(self):
        log.info(f'Logged in as {self.user} (ID: {self.user.id})')

    async def setup_hook(self):
        #cogs setup
        root_path = Path(__file__).parent.resolve().parent.resolve() 
        for file in root_path.glob('./src/cogs/*.py'):
            await self.load_extension(f'cogs.{file.name[:-3]}')

        #database setup
        await self.create_database_pool()
        await self.load_data()

        #wavelink setup
        node: wavelink.Node = wavelink.Node(
            uri='http://' + getenv('LAVALINK_HOST') + ':' + getenv('LAVALINK_PORT'), 
            password=getenv('LAVALINK_PASSWORD')
            )
        
        await wavelink.NodePool.connect(client=self, nodes=[node])

        #sync new commands
        await self.tree.sync()

    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            log.warn(error)
            await interaction.response.send_message(str(error), ephemeral=True)

        else:
            log.critical('Ignoring exception in command {}:'.format(error))
            await interaction.response.send_message(str(error), ephemeral=True)

    async def close(self):
        log.info(f'{len(self.voice_clients)} Voice Clients to shutdown')
        for voice in self.voice_clients:
            self.get_cog("Disconnect").stop_voice_functions(voice)

        if self.database is not None:
            await self.database.close()
            log.info("Database shutdown")

        await super().close()

    def get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        return intents

    async def create_database_pool(self) -> None:
        try:
            self.database: asyncpg.Pool = await asyncpg.create_pool(
            database=getenv('DATABASE_DATABASE'),
            user=getenv('DATABASE_USER'),
            host=getenv('DATABASE_HOST'),
            port=getenv('DATABASE_PORT'),
            password=getenv('DATABASE_PASSWORD')
            )

        except: #TODO add a exeception here
            log.critical("Database not connected")
            self.database = None #since it failed
            exit()

        log.info("Database connected")

    async def load_data(self) -> None:
        """Loads the entire table entry by entry into cache"""
        records = await self.database.fetch('SELECT * FROM guilds')

        for record in records:
            self.cache[record['guild_id']].music_channel_id = record['music_channel_id']
            self.cache[record['guild_id']].music_role_id = record['music_role_id']
            self.cache[record['guild_id']].volume = record['volume']

        log.info("Database loaded into cache")

    async def get_voice(self, guild_id: int, interaction: discord.Interaction = None) -> wavelink.Player:
        voice: wavelink.Player = self.get_guild(guild_id).voice_client

        if voice is None: #not connected to voice
            await interaction.response.send_message("Nothing is playing")
            return None

        return voice
