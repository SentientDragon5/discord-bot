import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from.env file
load_dotenv()

# Get the bot token from the environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable not set.")


intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content (if needed for other commands)

bot = commands.Bot(command_prefix="!", intents=intents)  # You can change the prefix


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync() # Sync slash commands globally. For guild specific use guild id in sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.tree.command(name="hello", description="Says hello!")
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world!")


# Example of a regular command (using prefix)
@bot.command()
async def hello_prefix(ctx):
    await ctx.send("Hello, world! (using prefix)")


bot.run(TOKEN)