import re
from math import floor

import discord

async def able_to_use_commands(interaction: discord.Interaction, is_playing: bool, music_channel_id, music_role_id) -> bool:
    """returns True if the user mets all conditions to use playing commands"""
    if music_role_id is not None:
        if interaction.user.get_role(music_role_id) is None: #true if user has correct role
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
                await voice.disconnect() #TODO use the `move_to` function
                return True

    return True

async def edit_view_message(bot, guild_id: int, change_to):
    playing_view_message = bot.get_channel(bot.cache[guild_id].playing_view_channel_id).get_partial_message(bot.cache[guild_id].playing_view_message_id)
    await playing_view_message.edit(view=change_to)

async def get_milliseconds_from_string(time_string: str, interaction: discord.Interaction) -> int:
    "takes a time string and returns the time in milliseconds `1:34` -> `94000`, errors return `-1`"
    TIME_RE = re.compile("^[0-5]?\d:[0-5]?\d:[0-5]\d|[0-5]?\d:[0-5]\d|\d+$")
    if not TIME_RE.match(time_string):
        await interaction.response.send_message("Invalid time stamp")
        return -1 #TODO maybe turn this into a exception 

    list_of_units = [int(x) for x in time_string.split(":")]

    list_of_units.reverse() #makes time more predictable to deal with
    total_seconds = 0
    if len(list_of_units) == 3: #hours
        total_seconds += (list_of_units[2] * 3600) #seconds in an hour

    if len(list_of_units) == 2: #minutes
        total_seconds += (list_of_units[1] * 60)

    total_seconds += list_of_units[0] #total seconds

    return (total_seconds * 1000) #turn into milliseconds

def seconds_to_timestring(total_seconds: int) -> str:
    """Takes the total amount of seconds and returns a time like `1:35:54` or `1:23`"""
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f'{(floor(hours)):02}:{(floor(minutes)):02}:{(floor(seconds)):02}'

    return f'{(floor(minutes)):02}:{(floor(seconds)):02}'
