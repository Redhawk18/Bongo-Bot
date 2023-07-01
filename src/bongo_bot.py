from collections import defaultdict
import logging
from os import getenv
from math import floor
from pathlib import Path
import sys
import traceback

import asyncpg
import discord
from discord.ext import commands
import wavelink

from cache import Cache

log = logging.getLogger(__name__)


class Bongo_Bot(commands.Bot):
    """Handles intents, prefixs, and database init automatically"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix="!", intents=self.get_intents(), *args, **kwargs
        )
        self.tree.on_error = self.on_tree_error

        self.cache = defaultdict(Cache)

    async def close(self):
        log.info(f"{len(self.voice_clients)} Voice Clients to shutdown")
        for voice in self.voice_clients:
            self.get_cog("Disconnect").stop_voice_functions(voice)

        if self.database is not None:
            await self.database.close()
            log.info("Database shutdown")

        await super().close()

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            log.warn(error)
            await interaction.response.send_message(str(error), ephemeral=True)

        else:
            log.critical("Ignoring exception in command {}:".format(error))
            traceback.print_exception(type(error), error, error.__traceback__)
            await interaction.response.send_message(str(error), ephemeral=True)

    async def setup_hook(self):
        # cogs setup
        root_path = Path(__file__).parent.resolve().parent.resolve()
        for file in root_path.glob("./src/cogs/*.py"):
            await self.load_extension(f"cogs.{file.name[:-3]}")

        # database setup
        await self.create_database_pool()
        await self.load_data()

        # wavelink setup
        node: wavelink.Node = wavelink.Node(
            uri="http://" + getenv("LAVALINK_HOST") + ":" + getenv("LAVALINK_PORT"),
            password=getenv("LAVALINK_PASSWORD"),
        )
        await wavelink.NodePool.connect(client=self, nodes=[node])

        # sync new commands
        await self.tree.sync()

    async def able_to_use_commands(
        self,
        interaction: discord.Interaction,
        music_channel_id,
        music_role_id,
    ) -> bool:
        """returns True if the user mets all conditions to use playing commands"""
        if music_role_id is not None:
            if (
                interaction.user.get_role(music_role_id) is None
            ):  # true if user has correct role
                await interaction.response.send_message(
                    f"User does not have music role"
                )
                return False

        if interaction.channel_id != music_channel_id and music_channel_id is not None:
            await interaction.response.send_message(f"Wrong channel for music")
            return False

        if interaction.user.voice is None:  # not in any voice chat
            await interaction.response.send_message("Not in any voice chat")
            return False

        if interaction.user.voice.deaf or interaction.user.voice.self_deaf:  # deafen
            await interaction.response.send_message(
                "Deafed users can not use playing commands"
            )
            return False

        voice = interaction.guild.voice_client
        if voice is not None:
            if (
                voice.channel.id != interaction.user.voice.channel.id
            ):  # bot is in a different voice chat than user
                if is_playing:  # bot is busy
                    await interaction.response.send_message(
                        "Not in the same voice channel"
                    )
                    return False

                elif not is_playing:  # bot is idling
                    await voice.disconnect()  # TODO use the `move_to` function
                    return True

        return True

    async def create_database_pool(self) -> None:
        try:
            self.database: asyncpg.Pool = await asyncpg.create_pool(
                database=getenv("DATABASE_DATABASE"),
                user=getenv("DATABASE_USER"),
                host=getenv("DATABASE_HOST"),
                port=getenv("DATABASE_PORT"),
                password=getenv("DATABASE_PASSWORD"),
            )

        except:  # TODO add a exeception here
            log.critical("Database not connected")
            self.database = None  # since it failed
            exit()

        log.info("Database connected")

    async def edit_view_message(self, guild_id: int, change_to):
        await self.cache[guild_id].playing_view_message.edit(view=change_to)

    def get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        return intents

    async def get_player(self, interaction: discord.Interaction) -> wavelink.Player:
        player: wavelink.Player = interaction.guild.voice_client

        if player is None:  # not connected to voice
            await interaction.response.send_message("Nothing is playing")
            return None

        return player

    async def load_data(self) -> None:
        """Loads the entire table entry by entry into cache"""
        records = await self.database.fetch("SELECT * FROM guilds")

        for record in records:
            self.cache[record["guild_id"]].music_channel_id = record["music_channel_id"]
            self.cache[record["guild_id"]].music_role_id = record["music_role_id"]
            self.cache[record["guild_id"]].volume = record["volume"]

        log.info("Database loaded into cache")

    def seconds_to_timestring(self, total_seconds: int) -> str:
        """Takes the total amount of seconds and returns a time like `1:35:54` or `1:23`"""
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{(floor(hours)):02}:{(floor(minutes)):02}:{(floor(seconds)):02}"

        return f"{(floor(minutes)):02}:{(floor(seconds)):02}"
