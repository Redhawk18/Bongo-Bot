from math import ceil
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

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
        await interaction.response.send_message(f'**Pong!** 🏓 {ceil(self.bot.latency*1000)}ms')

    @commands.Cog.listener()
    async def on_message(self, message):
        TROLLED_USER_ID = int(os.getenv('TROLLED_USER_ID'))

        if TROLLED_USER_ID == message.author.id:
            if random.randint(1, 50) == 1:
                await message.add_reaction("🐧")

    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("test", view=Playing_View(self.bot))


async def setup(bot):
    await bot.add_cog(Frank(bot))

class Playing_View(discord.ui.View):
    """The view for the playing output"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
        self.add_items(True)

    def add_items(self, is_pause):
        self.clear_items() 

        if is_pause:
            self.add_item(self.pause)
        else: 
            self.add_item(self.resume)

        self.add_item(self.skip)
        self.add_item(self.now_playing)
        self.add_item(self.loop)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="⏸")
    async def pause(self, interaction, button):
        #await self.bot.get_cog("Pause").helper(interaction)
        self.add_items(False)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.gray, emoji="▶️")
    async def resume(self, interaction: discord.Interaction, button):
        await self.bot.get_cog("Resume").helper(interaction)
        self.add_items(True)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.gray, emoji="⏭")
    async def skip(self, interaction, button):
        await self.bot.get_cog("Skip").helper(interaction)

    @discord.ui.button(label="Now Playing", style=discord.ButtonStyle.gray, emoji="🎶")
    async def now_playing(self, interaction, button):
        await self.bot.get_cog("Now_Playing").helper(interaction)

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.gray, emoji="🔁")
    async def loop(self, interaction, button):
        await self.bot.get_cog("Loop").helper(interaction)