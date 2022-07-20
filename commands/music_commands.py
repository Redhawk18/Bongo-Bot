import asyncio
from collections import deque
from math import floor

import wavelink
import discord
from discord import app_commands
from discord.ext import commands

class Music_Commands(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.song_queue = deque()
        self.is_playing = False 
        self.now_playing:dict = None




    @commands.Cog.listener()
    async def on_ready(self):
        print("music commands lister online")


    #Lavalink 
    async def cog_load(self):
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="password"
        )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        print("start of track")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.player, track: wavelink.Track, reason):
        print("end of track")


    async def play2(self, vc: wavelink.Player, interaction, *, track: wavelink.YouTubeTrack):
        print("in func")

             


    @app_commands.command()
    async def play(self, interaction: discord.Interaction, *, query: str): #TODO add parsing for direct urls
        """Play a song with the given search query.

        If not connected, connect to our voice channel.
        """
        if not interaction.guild.voice_client:
            vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)

        else:
            vc: wavelink.Player = interaction.guild.voice_client

        track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        await interaction.response.send_message(f"**Playing** :notes: `{track.title}` by `{track.author}` - Now!")   
        await vc.play(track)


    @app_commands.command(name="pause", description="Pauses track")
    async def pause(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.is_playing():
            await voice.pause()
            await interaction.response.send_message("**Paused** :pause_button:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name="resume", description="Resumes track")
    async def resume(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.is_paused():
            await voice.resume()
            await interaction.response.send_message("**Resumed** :arrow_forward:")

        else:
            await interaction.response.send_message("Nothing is paused")


    @app_commands.command(name="force-skip", description="Skips the track")
    async def forceskip(self, interaction: discord.Interaction):
        voice: wavelink.Player = interaction.guild.voice_client
        
        if voice.is_playing():
            self.how_many_want_to_skip = 0 #reset counter
            await voice.stop()
            await interaction.response.send_message("**Skipped** :fast_forward:")

        else:
            await interaction.response.send_message("Nothing is playing")


    @app_commands.command(name='skip', description='Calls a vote to skip the track')
    async def skip(self, interaction: discord.Interaction):
        if not await self._in_voice_channel(interaction):
            return
        voice = interaction.guild.voice_client

        if voice.is_playing():
            #increase the how_many_want_to_skip
            self.how_many_want_to_skip += 1

            #check if its passed threshold
            voice_channel = interaction.message.author.voice.channel
            threshold = floor((len(voice_channel.members)-1)/2) #-1 for the bot

            if self.how_many_want_to_skip >= threshold: #enough people
                await self.forceskip(interaction)
            
            else: #not enough people
                await interaction.response.send_message(f'**Skipping? ({self.how_many_want_to_skip}/{threshold} people) or use `forceskip`**')

        else:
            await interaction.response.send_message("Nothing is playing")
            return


    









































async def setup(bot):
    await bot.add_cog(Music_Commands(bot))