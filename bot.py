# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

import google.generativeai as genai


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Specify intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents) 

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    convo_hist.append(f"{message.author.global_name} : {message.content}")
    if "/a" in message.content:
        print("asked : ", message.content)

        response = model.generate_content(convo_hist)
        print("responded: ", response.text)
        await message.channel.send(response.text)

convo_hist = []
# def add_message_to_convo(message):
#     convo_hist.append(message.author.)

client.run(TOKEN)