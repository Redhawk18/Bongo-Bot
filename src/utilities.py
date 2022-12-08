import re

import discord

from custom_player import Custom_Player

async def able_to_use_commands(interaction: discord.Interaction, is_playing: bool, music_channel_id, music_role_id) -> bool: #
    """returns True if the user mets all conditions to use playing commands"""
    if interaction.user.get_role(music_role_id) is not None:
        await interaction.response.send_message(f'User does not have music role')
        return False

    if interaction.channel_id != music_channel_id and music_channel_id is not None:
        await interaction.response.send_message(f'Wrong channel for music')
        return False

    if interaction.user.voice is None: #not in any voice chat
        await interaction.response.send_message("Not in any voice chat")
        return False

    if interaction.user.voice.deaf or interaction.user.voice.self_deaf: #deafen
        await interaction.response.send_message("Deafed users can not use playing commands")
        return False

    voice = interaction.guild.voice_client
    if voice is not None:
        if voice.channel.id != interaction.user.voice.channel.id: #bot is in a different voice chat than user
            if is_playing: #bot is busy
                await interaction.response.send_message("Not in the same voice channel")
                return False

            elif not is_playing: #bot is idling
                await voice.disconnect()
                return True

    return True

def add_zero(number) -> str:
    """turns 2 seconds to 02"""
    if number < 10:
        return "0" + str(number)

    return str(number)

async def get_milliseconds_from_string(time_string: str, interaction: discord.Interaction) -> int:
    "takes a time string and returns the time in milliseconds `1:34` -> `94000`, errors return `-1`"
    TIME_RE = re.compile("^[0-5]?\d:[0-5]?\d:[0-5]\d|[0-5]?\d:[0-5]\d|\d+$")
    if not TIME_RE.match(time_string):
        await interaction.response.send_message("Invalid time stamp")
        return -1

    list_of_units = [int(x) for x in time_string.split(":")]

    list_of_units.reverse() #makes time more predictable to deal with
    total_seconds = 0
    if len(list_of_units) == 3: #hours
        total_seconds += (list_of_units[2] * 3600) #seconds in an hour

    if len(list_of_units) == 2: #minutes
        total_seconds += (list_of_units[1] * 60)

    total_seconds += list_of_units[0] #total seconds

    return (total_seconds * 1000) #turn into milliseconds

async def get_voice(interaction) -> Custom_Player:
    voice: Custom_Player = interaction.guild.voice_client

    if voice is None: #not connected to voice
        await interaction.response.send_message("Nothing is playing")
        return None

    return voice
