import discord
from discord.ext import commands
from datetime import datetime
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

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

used_dates = {}

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
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ That command does not exist. Use `$help` to see available commands.")
    else:
        raise error  # Raise other errors normally

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")

@bot.command()
async def test(ctx):
    await ctx.send(f"Bot is running!")

# Bulk delete command
@bot.command()
@commands.has_permissions(manage_messages=True)  # Ensure the user has the 'Manage Messages' permission
async def delete(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("Please specify a number between 1 and 100.")
        return

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f'Deleted {len(deleted)} message(s).', delete_after=5)  # Message will auto-delete after 5 seconds


# About command with embed
@bot.command()
async def about(ctx):
    embed = discord.Embed(
        title="About This Bot",
        description="Here is some information about me!",
        color=discord.Color.blue()  # You can change this to any color you like
    )

    embed.add_field(name="Bot Name", value="The PR Bot", inline=False)
    embed.add_field(name="Version", value="1.0.0", inline=False)
    embed.add_field(name="Creator", value="the.username_", inline=False)
    embed.add_field(name="Description", value="Serving the PR department", inline=False)

    await ctx.send(embed=embed)

#ping command
@bot.command()
async def ping(ctx):
    """
    Responds with 'Pong!' and the bot's latency in ms.
    """
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds
    await ctx.send(f"Pong! Latency: {latency}ms")

#Appeal Command Modal
class AppealModal(discord.ui.Modal, title="Appeal Form"):
    username = discord.ui.TextInput(label="Username", placeholder="Enter your username", required=True)
    appeal = discord.ui.TextInput(label="Decision Being Appealed", placeholder="Ban/Termination/Resignation/Demotion", required=True)
    date = discord.ui.TextInput(label="Date of Punishment", placeholder="Enter the date of Resignation, Ban, etc. (YYYY-MM-DD)", required=True)
    reason = discord.ui.TextInput(label="Reason for Appeal", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        log_channel_id = 1348299280959668254  # Replace with your channel ID
        log_channel = interaction.client.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title="New Appeal Submission", color=discord.Color.blue())
            embed.add_field(name="Username", value=self.username.value, inline=True)
            embed.add_field(name="Date", value=self.date.value, inline=True)
            embed.add_field(name="Appeal Type", value=self.appeal.value, inline=True)
            embed.add_field(name="Reason for Appeal", value=self.reason.value, inline=False)
            embed.set_footer(text=f"Submitted by {interaction.user} (ID: {interaction.user.id})")

            await log_channel.send(embed=embed)

        await interaction.response.send_message("✅ Appeal submitted successfully!", ephemeral=True)

@bot.tree.command(name="appeal", description="Open the appeal form")
async def appeal(interaction: discord.Interaction):
    await interaction.response.send_modal(AppealModal())

#OTD Modal
class OTD(discord.ui.Modal, title="OTD Form"):
    username = discord.ui.TextInput(label="Username", placeholder="Enter your username", required=True)
    otd = discord.ui.TextInput(label="OTD Style", placeholder="QOTD, ROTD, FOTD, etc.", required=True)
    date = discord.ui.TextInput(label="Date of OTD (YYYY-MM-DD)", placeholder="Date of publish", required=True)
    description = discord.ui.TextInput(label="Description of OTD", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        log_channel_id = 1338640533572030504  # Replace with your channel ID
        log_channel = interaction.client.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title="New OTD Submission", color=discord.Color.blue())
            
            # Use `.value` to access the input values
            embed.add_field(name="Username", value=self.username.value, inline=True)
            embed.add_field(name="OTD Style", value=self.otd.value, inline=True)
            embed.add_field(name="Date of OTD", value=self.date.value, inline=True)
            embed.add_field(name="Description", value=self.description.value, inline=False)
            
            embed.set_footer(text=f"Submitted by {interaction.user} (ID: {interaction.user.id})")
            
            await log_channel.send(embed=embed)

        await interaction.response.send_message("✅ OTD submitted successfully!", ephemeral=True)

# Correctly instantiate the modal in the command
@bot.tree.command(name="appeal", description="Open the appeal form")
async def appeal(interaction: discord.Interaction):
    await interaction.response.send_modal(OTD())

# Run the bot with your token
bot.run(os.getenv("TOKEN"))  # Fetches token securely from Render
