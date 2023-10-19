import logging

from discord.ext import commands

import bongo_bot

log = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        log.info(f"Inserting guild {guild.name} {guild.id}")
        await self.bot.database.execute(f"INSERT INTO guilds VALUES ({guild.id});")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log.info(f"Deleting guild {guild.name} {guild.id}")
        await self.bot.database.execute(
            f"DELETE FROM guilds WHERE guild_id = {guild.id};"
        )


async def setup(bot):
    await bot.add_cog(Events(bot))
