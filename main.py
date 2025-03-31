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

#OTD Modal
class otd_modal(discord.ui.Modal, title="OTD Form"):
    username = discord.ui.TextInput(label="Username", placeholder="Enter your username", required=True)
    otd = discord.ui.TextInput(label="OTD Style", placeholder="QOTD, ROTD, FOTD, etc.", required=True)
    date = discord.ui.TextInput(label="Date of OTD (YYYY-MM-DD)", placeholder="Date of publish", required=True)
    description = discord.ui.TextInput(label="Description of OTD", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Access log channel
            log_channel_id = 1338640533572030504  # Replace with your channel ID
            log_channel = interaction.client.get_channel(log_channel_id)
            
            if not log_channel:
                raise ValueError("Log channel not found.")
            
            # Create embed for the OTD submission
            embed = discord.Embed(title="New OTD Submission", color=discord.Color.blue())
            embed.add_field(name="Username", value=self.username.value, inline=True)
            embed.add_field(name="OTD Style", value=self.otd.value, inline=True)
            embed.add_field(name="Date of OTD", value=self.date.value.strftime("%B %d, %Y"), inline=True)
            embed.add_field(name="Description", value=self.description.value, inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} (ID: {interaction.user.id})")
            
            # Send the embed to the log channel
            await log_channel.send(embed=embed)
            
            # Send success message to the user
            await interaction.response.send_message("✅ OTD submitted successfully!", ephemeral=True)
        
        except Exception as e:
            # Log the error and notify the user
            print(f"Error while handling OTD modal submission: {e}")
            await interaction.response.send_message(f"❌ An error occurred while processing your OTD submission: {str(e)}", ephemeral=True)

@bot.tree.command(name="otd", description="Open the OTD form")
async def otd(interaction: discord.Interaction):
    await interaction.response.send_modal(otd_modal())

# Run the bot
bot.run(os.getenv('TOKEN'))  # Get token from environment variable
