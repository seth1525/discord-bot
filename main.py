import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# Initialize Flask
app = Flask(__name__)

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask endpoint for uptime monitoring
@app.route('/')
def home():
    return "Bot is running!"

# Function to keep the Flask app running in a separate thread
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask in a separate thread
thread = Thread(target=run_flask)
thread.start()

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
