import discord

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

    async def edit_view(self, interaction: discord.Interaction, is_pause: bool):
        message_id = interaction.message.id
        self.add_items(is_pause)
        await interaction.followup.edit_message(message_id, view=self)

    def get_view(self):
        return self

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="⏸")
    async def pause(self, interaction: discord.Interaction, button):
        await self.bot.get_cog("Pause").helper(interaction)
        await self.edit_view(interaction, False)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.gray, emoji="▶️")
    async def resume(self, interaction: discord.Interaction, button):
        await self.bot.get_cog("Resume").helper(interaction)
        await self.edit_view(interaction, True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.gray, emoji="⏭")
    async def skip(self, interaction, button):
        await self.bot.get_cog("Skip").helper(interaction)

    @discord.ui.button(label="Now Playing", style=discord.ButtonStyle.gray, emoji="🎶")
    async def now_playing(self, interaction, button):
        await self.bot.get_cog("Now_Playing").helper(interaction)

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.gray, emoji="🔁")
    async def loop(self, interaction, button):
        await self.bot.get_cog("Loop").helper(interaction)
