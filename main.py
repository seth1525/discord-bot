import discord
from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"  # Simple response to show server is working

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Syncing commands...")
    try:
        await bot.tree.sync()  # Sync slash commands
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred in event: {event}")
    raise  # Optional: You can raise the error again if you want it to show in the console or log file

#Ping Command
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    # Respond with "Pong!" and the latency (in milliseconds)
    await interaction.response.send_message(f"Pong! Latency is {bot.latency * 1000:.2f}ms")

# Run the bot with your token
bot.run(os.getenv("TOKEN"))  # Fetches token securely from Render
