import discord
from flask import Flask
from threading import Thread
import os

# Flask setup for UptimeRobot monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Discord bot setup
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred in event: {event}")
    raise  # Optional: Raise the error for debugging

# Ping command
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency is {bot.latency * 1000:.2f}ms")

# Run the bot
bot.run(os.getenv("TOKEN"))
