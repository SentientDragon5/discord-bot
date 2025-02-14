import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

intents = discord.Intents.default()
intents.message_content = True  # If you need to read message content
intents.voice_states = True # Required to get voice channel information

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.tree.command(name="join", description="Joins the 'General' voice channel.")
async def join_voice(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        if guild is None: # Interaction is not in a guild (DM)
            await interaction.response.send_message("This command can only be used in a server.")
            return

        general_channel = discord.utils.get(guild.voice_channels, name="General")

        if general_channel is None:
            await interaction.response.send_message("The 'General' voice channel was not found.")
            return

        if guild.voice_client: # Bot is already in a voice channel
            if guild.voice_client.channel == general_channel: # Already in the correct channel
                await interaction.response.send_message("Already in the 'General' voice channel.")
                return
            await guild.voice_client.move_to(general_channel) # Move to the general channel
            await interaction.response.send_message(f"Moved to the 'General' voice channel.")
            return

        await general_channel.connect()
        await interaction.response.send_message(f"Joined the 'General' voice channel.")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")


@bot.tree.command(name="leave", description="Leaves the current voice channel.")
async def leave_voice(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("This command can only be used in a server.")
            return

        if guild.voice_client:
            await guild.voice_client.disconnect()
            await interaction.response.send_message("Left the voice channel.")
        else:
            await interaction.response.send_message("Not currently in a voice channel.")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")



bot.run(TOKEN)