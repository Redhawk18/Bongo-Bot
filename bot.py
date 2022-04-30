import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
#print(os.getenv('DISCORD_TOKEN'))
TOKEN = os.getenv('DISCORD_TOKEN')
TROLLED = os.getenv('TROLLED_USER')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'{client.user} is connected to the following guild:\n')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if str(message.author) == TROLLED:
        if '?' in message.content:
            await message.channel.send(":penguin:")
    
    epic_quotes = [
        'Mimosa is literally orihime',
        'Hi Ben jojolion isnt coming out till the 19th, feelsbadman\n Wait part 6 ended this month?\n part 6 ended in 2005',
        'hi guys\n Why\n https://tenor.com/view/xqc-arabfunny-arabic-saudi-arabia-projared-gif-18306091',
    ]    
        
    if message.content == 'quote':
        response = random.choice(epic_quotes)
        await message.channel.send(response)

client.run(TOKEN)