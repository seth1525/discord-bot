import discord
from discord.ext import commands
import os

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred in event: {event}")
    raise  # Optional: Raise the error for debugging

# Ping command
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency is {bot.latency * 1000:.2f}ms")

# Run the bot
bot.run(os.getenv('TOKEN'))  # Get token from environment variable
