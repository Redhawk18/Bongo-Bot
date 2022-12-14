from dotenv import load_dotenv
import os
import random

from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        #get trolled user from env
        load_dotenv() #this should not be here
        TROLLED_USER_ID = int(os.getenv('TROLLED_USER_ID'))

        if TROLLED_USER_ID == message.author.id:
            if random.randint(1, 20) == 1: #1 in 20 messages
                await message.add_reaction("🐧")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        #add guild id to database
        await self.bot.database.execute(f'INSERT INTO guilds VALUES ({guild.id});')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        #remove guild id from database
        await self.bot.database.execute(f'DELETE FROM guilds WHERE guild_id = {guild.id};')

async def setup(bot):
    await bot.add_cog(Events(bot))
