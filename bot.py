import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

import google.generativeai as genai

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    # No need to sync slash commands if you're not using them
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

convo_hist = [
    "System: You are Nagol. you are evil and love to make puns. you speak in limericks"  # Initial system prompt
]

@bot.event
async def on_message(message):
    if message.author == bot.user:  # Check if the message is from the bot itself
        return

    user_message = message.content # Convert to lowercase for easier checking

    if "/a" in user_message:
        question = user_message.split("/a", 1)[1]  # Extract the question
        convo_hist.append(f"{message.author.global_name}: {question}")
        print("asked: ", question)
        generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p = 0.95,
            candidate_count=1,
            max_output_tokens=2048
        )

        response = model.generate_content(
            convo_hist,
            generation_config=generation_config
        )
        print("responded: ", response.text)
        await message.channel.send(response.text)

    elif "/c" in user_message:
        convo_hist.clear()
        await message.channel.send("Conversation history cleared.")
    elif "/d" in user_message:
        convo_hist.clear()
        await message.channel.send("Conversation history:\n" + str(convo_hist))
    else :
        convo_hist.append(f"{message.author.global_name}: {message.content}")

bot.run(TOKEN)