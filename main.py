import discord
from flask import Flask
from threading import Thread
import os

bot = discord.Bot()

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
            embed.add_field(name="Date of OTD", value=self.date.value, inline=True)
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

#Ping Command
@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    # Respond with "Pong!" and the latency (in milliseconds)
    await interaction.response.send_message(f"Pong! Latency is {bot.latency * 1000:.2f}ms")

# Run the bot with your token
bot.run(os.getenv("TOKEN"))  # Fetches token securely from Render
