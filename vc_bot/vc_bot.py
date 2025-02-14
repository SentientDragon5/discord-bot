# Import necessary libraries
import discord
from discord.ext import commands
import dotenv
import os
import asyncio
import speech_recognition as sr
from io import BytesIO
from discord import ClientException, User  # Import ClientException
from discord.sinks import Sink  # Import from discord.sinks


# Load environment variables from .env file
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents.  Enable voice states and message content.
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Initialize the bot with the specified intents and command prefix
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Load Opus (required for voice functionality)
if not discord.opus.is_loaded():
    try:
        # Try multiple common names and paths for libopus
        for opus_library in ['opus', 'libopus.so.0', 'libopus.0.dylib', '/usr/local/lib/libopus.0.dylib', '/opt/homebrew/lib/libopus.0.dylib']:
            try:
                discord.opus.load_opus(opus_library)
                print(f"Opus loaded successfully from: {opus_library}")
                break  # Stop searching if successful
            except OSError:
                continue  # Try the next library name/path
        else:  # This 'else' clause runs if the loop completes without breaking
            raise OSError("Could not find a suitable libopus library.")

    except OSError as e:
        print(f"Failed to load Opus: {e}")
        print("Voice functionality will not work.")
        # Consider exiting or disabling voice commands here

@bot.event
async def on_ready():
    """
    Event handler: Called when the bot is ready and connected to Discord.
    """
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    await bot.sync_commands()  # Sync slash commands
    print("Commands synced.")
    print("------")

async def process_audio(audio_bytes, user_id: int): #Type hint
    """
    Processes the given audio data and prints the transcribed text.

    Args:
        audio_bytes: The audio data to transcribe (raw bytes).
        user_id: discord user ID (integer)
    """
    try:
        # Convert the raw bytes to an in-memory file-like object
        with BytesIO(audio_bytes) as audio_file:
            # Create an AudioFile object from the in-memory file
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)  # Read the audio data

        text = recognizer.recognize_google(audio) # use google recognizer as an example

        # Get the user object from the ID
        user: User = bot.get_user(user_id) # Use type hint and assignment
        if user:  # Check if the user was found
             print(f"Transcription for {user.name}: {text}")
        else:
            print(f"Transcription for user ID {user_id}: {text}")
            print(f"Could not retrieve user object for ID {user_id}")

    except sr.UnknownValueError:
        print(f"Could not understand audio for user ID: {user_id}")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service for user ID {user_id}; {e}")
    except Exception as e:
        print(f"An error occurred while processing for user ID {user_id}: {e}")

class MySink(Sink):
    """
    Custom AudioSink to receive and process audio data.
    """
    def __init__(self):
        super().__init__()
        self.audio_data = {}

    async def write(self, data, user_id):
        """
        Receives audio data from Discord.

        Args:
            data: The raw PCM audio data.
            user_id: The ID of the user sending the audio.
        """
        if user_id not in self.audio_data:
          self.audio_data[user_id] = bytearray()
        self.audio_data[user_id].extend(data)
        await process_audio(bytes(self.audio_data[user_id]), user_id)
        self.audio_data[user_id].clear()


    async def on_close(self):
        """
        Performs cleanup (if needed).
        """
        self.audio_data = {}
        print("AudioSink cleanup complete.")

async def _record_callback(sink: Sink, ctx: commands.Context):
    """
    This callback is called when the recording is stopped.
    """
    # Get the voice client from the context
    voice_client = ctx.voice_client

    if voice_client:
      print(f"Finished recording in {ctx.guild.name}")


@bot.slash_command(name="join", description="Joins the voice channel you are in.")
async def join(ctx: discord.ApplicationContext):
    """
    Slash command: Makes the bot join the user's voice channel.
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            voice_client: discord.VoiceClient = await channel.connect() #type hint
        except ClientException as e:
            await ctx.respond(f"Error connecting: {e}")
            return

        sink = MySink()
        voice_client.start_recording(sink, _record_callback, ctx)

        await ctx.respond(f"Joined {channel.name}.")

    else:
        await ctx.respond("You are not in a voice channel.")



@bot.slash_command(name="leave", description="Leaves the voice channel.")
async def leave(ctx: discord.ApplicationContext):
    """
    Slash command: Makes the bot leave the current voice channel.
    """
    voice_client = ctx.guild.voice_client
    if voice_client:
        voice_client.stop_recording()
        await voice_client.disconnect()
        await ctx.respond("Left the voice channel.")
    else:
        await ctx.respond("I am not in a voice channel.")


@bot.event
async def on_voice_state_update(member, before, after):
    """
    Handles voice state updates.
    """
    if before.channel is not None and bot.user in before.channel.members:
        if len(before.channel.members) == 1 and before.channel.members[0] == bot.user:
            voice_client = before.channel.guild.voice_client
            if voice_client:
                voice_client.stop_recording()
                await voice_client.disconnect()
                print(f"Bot disconnected from {before.channel.name} (empty channel).")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user: return
    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)