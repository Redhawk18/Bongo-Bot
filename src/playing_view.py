import discord

class Playing_View(discord.ui.View):
    """The view for the playing output"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot


    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="⏸")
    async def pause_callback(self, interaction, button):
        await self.bot.get_cog("Pause").helper(interaction)


    @discord.ui.button(label="Resume", style=discord.ButtonStyle.gray, emoji="▶️")
    async def resume_callback(self, interaction, button):
        await self.bot.get_cog("Resume").helper(interaction)


    @discord.ui.button(label="Skip", style=discord.ButtonStyle.gray, emoji="⏭")
    async def skip_callback(self, interaction, button):
        await self.bot.get_cog("Force_Skip").helper(interaction)


    @discord.ui.button(label="Now Playing", style=discord.ButtonStyle.gray, emoji="🎶")
    async def now_playing_callback(self, interaction, button):
        await self.bot.get_cog("Now_Playing").helper(interaction)


    @discord.ui.button(label="Loop", style=discord.ButtonStyle.gray, emoji="🔁")
    async def loop_callback(self, interaction, button):
        await self.bot.get_cog("Loop").helper(interaction)