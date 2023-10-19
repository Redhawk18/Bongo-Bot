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
        log.info("Disconnecting Lavalink nodes")
        await wavelink.Pool.close()

        log.info(f"{len(self.voice_clients)} Voice Clients to shutdown")
        for voice in self.voice_clients:
            self.get_cog("Disconnect").stop_voice(voice)

        if hasattr(self, "database"):
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
        await wavelink.Pool.connect(client=self, nodes=[node])

        # sync new commands
        await self.tree.sync()

    async def able_to_use_commands(self, interaction: discord.Interaction) -> bool:
        """returns True if the user mets all conditions to use playing commands"""
        if self.cache[interaction.guild_id].music_role_id is not None:
            if (
                interaction.user.get_role(
                    self.cache[interaction.guild_id].music_role_id
                )
                is None
            ):  # true if user has correct role
                await interaction.response.send_message(
                    f"User does not have music role"
                )
                return False

        if (
            interaction.channel_id != self.cache[interaction.guild_id].music_channel_id
            and self.cache[interaction.guild_id].music_channel_id is not None
        ):
            await interaction.response.send_message(f"Wrong channel for music")
            return False

        if interaction.user.voice is None:  # not in any voice chat
            await interaction.response.send_message("Not in any voice channel")
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
                if voice.is_playing():  # bot is busy
                    await interaction.response.send_message(
                        "Not in the same voice channel"
                    )
                    return False

                else:  # bot is idling
                    await voice.move_to(interaction.user.voice.channel)
                    return True

        return True

    async def create_database_pool(self) -> None:
        try:
            self.database: asyncpg.Pool = await asyncpg.create_pool(
                database=getenv("POSTGRES_DATABASE"),
                user=getenv("POSTGRES_USER"),
                host=getenv("POSTGRES_HOST"),
                port=getenv("POSTGRES_PORT"),
                password=getenv("POSTGRES_PASSWORD"),
            )

        except Exception as e:  # TODO add a exeception here
            log.critical("Database not connected")
            log.critical(e)
            self.database = None  # since it failed
            exit()

        log.info("Database connected")

    async def does_voice_exist(self, interaction: discord.Interaction) -> bool:
        if interaction.guild.voice_client:
            return True

        await interaction.response.send_message("Nothing is playing")
        return False

    async def edit_view_message(self, guild_id: int, view: discord.ui.View | None):
        voice = self.get_guild(guild_id).voice_client
        if voice is not None:
            await voice.message.edit(view=view)

    def get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.voice_states = True

        return intents

    async def get_player(self, interaction: discord.Interaction) -> wavelink.Player:
        player: wavelink.Player = interaction.guild.voice_client

        if player is None:
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

    def milliseconds_to_timestring(self, milliseconds: int) -> str:
        """Takes the total amount of milliseconds and returns a time like `1:35:54` or `1:23`"""
        seconds = milliseconds / 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{(floor(hours)):02}:{(floor(minutes)):02}:{(floor(seconds)):02}"

        return f"{(floor(minutes)):02}:{(floor(seconds)):02}"
