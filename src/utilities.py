import re

import discord

async def get_milliseconds_from_string(time_string: str, interaction: discord.Interaction):
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


async def add_zero(number):
    """turns 2 seconds to 02"""
    if number < 10:
        return "0" + str(number)

    return str(number)