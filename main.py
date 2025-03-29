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
    print(f'{bot.user} is online!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
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

# Event command
@bot.command()
async def otd(ctx, name: str, date: str, *, description: str):
    """
    Create an event with a name, date (MM-DD format), and description.
    Prevents duplicate dates in the same channel.

    Example: $otd "Game Night" "03-30" "Join us for an exciting game night!"

    Parameters:
    - ctx: Context of the command (Discord message info)
    - name: Name of the event
    - date: Date in MM-DD format
    - description: Details about the event
    """

    print(f"Received name: {name}")
    print(f"Received date: {date}")
    print(f"Received description: {description}")

    try:
        # Convert the date string to a datetime object
        event_date = datetime.strptime(date, '%m-%d')
        formatted_date = event_date.strftime('%m-%d')

        # Store used dates per channel
        channel_id = ctx.channel.id
        if channel_id not in used_dates:
            used_dates[channel_id] = set()

        # Check if the date is already used
        if formatted_date in used_dates[channel_id]:
            await ctx.send(f"❌ The date **{event_date.strftime('%B %d')}** has already been used. Please choose another date.")
            return

        # Add the date to the used set
        used_dates[channel_id].add(formatted_date)

        # Create an embed for the event
        embed = discord.Embed(
            title=f"**OTD Style: {name}**",
            description=description,  # Add the event description
            color=discord.Color.green()
        )

        # Display the date and creator
        embed.add_field(name="OTD Date", value=event_date.strftime('%B %d'), inline=False)
        embed.add_field(name="Created By", value=ctx.author.mention, inline=False)

        # Send the embed with event details
        await ctx.send(embed=embed)

    except ValueError:
        # Handle invalid date format error
        await ctx.send("❌ Invalid date format. Please use MM-DD (e.g., 03-30).")

@bot.command()
async def ping(ctx):
    """
    Responds with 'Pong!' and the bot's latency in ms.
    """
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds
    await ctx.send(f"Pong! Latency: {latency}ms")

@bot.tree.command(name="appeal", description="Submit an appeal with username, ID, and date.")
async def appeal(
    interaction: discord.Interaction,
    username: str,
    appeal_id: str,
    date: str
):
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
        await interaction.response.send_message(
            f"✅ Appeal submitted!\n"
            f"**Username:** {username}\n"
            f"**Appeal ID:** {appeal_id}\n"
            f"**Date:** {date}",
            ephemeral=True
        )
    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid date format. Please use `YYYY-MM-DD`.", ephemeral=True
        )

# Run the bot with your token
bot.run(os.getenv("TOKEN"))  # Fetches token securely from Render
