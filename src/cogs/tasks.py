import discord
from discord.ext import commands, tasks

class Tasks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        #start tasks
        self.disconnect_timer.start()
        self.set_status.start()

    @tasks.loop(minutes=10)
    async def disconnect_timer(self):
        for voice in self.bot.voice_clients:
            if len(voice.channel.members) < 2: #no one in voice besides the bot
                await self.bot.get_cog("Disconnect").stop_voice_functions(voice)

    @tasks.loop(hours=24)
    async def set_status(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(activity=discord.Game(name=f'Music in {len(self.bot.guilds)} Servers'))

async def setup(bot):
    await bot.add_cog(Tasks(bot))
