import os
import discord
from discord.ext import commands, tasks

bot_token = os.getenv("DISCORD_BOT_TOKEN")

target_member = None
target_name = None

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def nickname(ctx, member: discord.Member, *, new_nick: str):
    try:
        await member.edit(nick=new_nick)
    except discord.Forbidden:
        await ctx.send("I don't have permission to change that user's nickname.")
        
@bot.command()
async def stop_nickname(ctx):
    global target_member, target_name
    target_name = None
    target_member = None
    await ctx.send("Stopped Nickname Loop")
        
@tasks.loop(seconds=1)
async def repeated_task():
    global target_member, target_name
    try:
        if target_member and target_name:
            await target_member.edit(nick=target_name)
    except discord.Forbidden:
        print("Invalid Permissions!")
        target_name = None
        target_member = None


bot.run(bot_token)