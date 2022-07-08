from math import ceil
import random

import discord
from discord import app_commands
from discord.ext import commands

class Util_Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    
    @commands.Cog.listener()
    async def on_ready(self):
        print("util commands lister online")


    @commands.command() #TODO redo all of this with choices from 2.0
    async def helpp(self, ctx, category : str):
        if category.lower() == 'util' or category.lower() == 'utils' or category.lower() == 'utilities':
            embed = discord.Embed(
            title = "**Util Commands**",
            description = """
            `ping` - shows the current ping of the bot

            `roll` - roll the sided die inputed
                usage - `roll 6`
                aliases - `r`

            `multipleroll` - roll the sided die inputed the how ever many times rolled
                usage - `multipleroll 6 2`
                aliases - `multiroll, mroll, mr`
            """,
            color = discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            return

        elif category.lower() == 'music':
            embed = discord.Embed(
            title = "**Music Commands**",
            description = """
            `disconnect` - resets the queue and disconnects the bot

            `musicchannel` - sets the current text channel to only accept music commands from

            `play` - searchs youtube for a video and plays it through a voice channel
                usage - `play one piece opening 13`
                aliases - `p`

            `playnext` - the play command but the video played with it is placed in front of the queue
                usage - `playnext one piece opening 15`
                aliases - `playtop`

            `playurl` - play a url directly to a video or playlist
                useage - `playurl https://www.youtube.com/watch?v=zW1v0QBqTOs&list=PLD7NSS9oUY0T30WaolXWoFxIHB9Z4b3Ix&index=1`
                aliases - `purl, pu`

            `pause` - pauses the current playing audio

            `resume` - unpauses the current audio

            `forceskip` - skips the song
                aliases - `fs, fskip`

            `skip` - starts a vote to skip the song
                aliases - `s`

            `queue` - lists all the songs in the queue
                aliases - `q`

            `queueclear` - clears the queue

            `queueremove` - removes a tracknumber from the queue
                useage - `queueremove 5`

            `loop` - enables or disables repeating the next song
            """,
            color = discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        elif category.lower() == 'useless':
            embed = discord.Embed(
            title = "**Useless Commands**",
            description = """
            `quote` - responds with a quote

            `frank` - "to be frank"
            """,
            color = discord.Color.green(),
            )
            await ctx.send(embed=embed)
            return

        else:
            await ctx.send("please use `help utils` `help music` or `help useless`")
            return


    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'**Pong!** :ping_pong: {ceil(self.client.latency*1000)}ms')


    @app_commands.command()
    async def roll(self, interaction: discord.Interaction, max : int):
        if max < 1:
            await interaction.response.send_message("Input invalid")
            return


        await interaction.response.send_message(f'**Rolled** :game_die: {random.randint(1, max)} of a {max}-sided die')


    @app_commands.command()
    async def multipleroll(self, interaction: discord.Interaction, max : int, number_of_rolls : int):
        if number_of_rolls < 1 or max < 1 or number_of_rolls > 192:
            await interaction.response.send_message("Input invalid")
            return

        sum = 0
        output = f'A {max}-sided die was rolled {number_of_rolls} times\n'
        for i in range(number_of_rolls):
            current_roll = random.randint(1, max)
            sum += current_roll
            output += f'Rolled {current_roll} :game_die:\n'

        #sum print
        output += "\n"
        output += f'The sum is **{sum} of {number_of_rolls * max}**'

        embed = discord.Embed(
            title = "**Multiple Rolled** :game_die:",
            description = output,
            color = discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)



async def setup(client):
    await client.add_cog(Util_Commands(client))
