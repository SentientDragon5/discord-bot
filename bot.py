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

sys_prompt =  "System: You are Nagol. you are evil. you speak in limericks"
convo_hist = [sys_prompt]
generation_config = genai.GenerationConfig(
    temperature=0.7,
    top_p = 0.95,
    candidate_count=1,
    max_output_tokens=2048
)

# bot.user.global_name
# didnt work bc it is not defined until on ready
respond_prompt = f"I am {"Nagol"}. I prefer to only talk when asked questions. Based off the following conversation, should I speak up and respond? return only the text \"yes\" or \"no\" and nothing else."
respond_config = genai.GenerationConfig(
    temperature=0.01,
    top_p = 0.95,
    candidate_count=1,
    max_output_tokens=8
)

@bot.event
async def on_message(message):
    if message.author == bot.user:  # Check if the message is from the bot itself
        return
    
    user_message = message.content # Convert to lowercase for easier checking
    convo_hist.append(f"{message.author.global_name}: {user_message}")

    print(respond_prompt + " "+ str(convo_hist))
    wants_talk = model.generate_content(
        respond_prompt + " "+ str(convo_hist),
        generation_config=respond_config
    )
    print(wants_talk.text)

    if ("/a" in user_message) or ("yes" in wants_talk.text):
        # convo_hist.append(f"{message.author.global_name}: {question}")
        print("asked: ", user_message)
        
        response = model.generate_content(
            convo_hist,
            generation_config=generation_config
        )
        print("responded: ", response.text)
        convo_hist.append(f"{bot.user.global_name}: {response.text}")
        await message.channel.send(response.text)

    elif "/c" in user_message:
        convo_hist.clear()
        convo_hist.append(sys_prompt)
        await message.channel.send("Conversation history cleared.")
    elif "/d" in user_message:
        await message.channel.send("Conversation history:\n" + str(convo_hist))
    # else :
    #     convo_hist.append(f"{message.author.global_name}: {message.content}")

bot.run(TOKEN)