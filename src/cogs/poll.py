import discord
from discord import app_commands
from discord.ext import commands

import bongo_bot

class Poll(commands.Cog):
    def __init__(self, bot: bongo_bot.Bongo_Bot):
        self.bot = bot

    @app_commands.command(
        name="poll", description="creates a poll with emotes to vote by"
    )  # TODO if polls get brought to discord natively, ill delete this
    @app_commands.describe(title="the title of the poll")
    @app_commands.guild_only()
    async def poll(
        self,
        interaction: discord.Interaction,
        title: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
        option5: str = None,
        option6: str = None,
        option7: str = None,
        option8: str = None,
        option9: str = None,
        option10: str = None,
    ):
        # take every option and put it in a list to loop through
        options = []
        num_to_word = (
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟",
        )

        # required args
        options.append(option1)
        options.append(option2)

        # this is truly spaghetti code
        if option3 is not None:
            options.append(option3)
        if option4 is not None:
            options.append(option4)
        if option5 is not None:
            options.append(option5)
        if option6 is not None:
            options.append(option6)
        if option7 is not None:
            options.append(option7)
        if option8 is not None:
            options.append(option8)
        if option9 is not None:
            options.append(option9)
        if option10 is not None:
            options.append(option10)

        # loop through valid options and create a string for embed
        description = ""
        index = 0
        for item in options:
            description += num_to_word[index] + " : " + item + "\n\n"
            index += 1

        # create embed with those options left
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

        # add reactions for each valid option left
        message = await interaction.original_response()
        for index in range(len(options)):
            await message.add_reaction(num_to_word[index])


async def setup(bot):
    await bot.add_cog(Poll(bot))
