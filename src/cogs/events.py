from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # add guild id to database
        await self.bot.database.execute(f"INSERT INTO guilds VALUES ({guild.id});")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # remove guild id from database
        await self.bot.database.execute(
            f"DELETE FROM guilds WHERE guild_id = {guild.id};"
        )


async def setup(bot):
    await bot.add_cog(Events(bot))
