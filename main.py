#https://discord.com/api/oauth2/authorize?client_id=1043544428486340748&permissions=8&scope=bot

import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import pymongo


load_dotenv()

cluster = pymongo.MongoClient(os.getenv("db"))
db = cluster[os.getenv("board")]
lmao=db["lmao_counter"]


intents=nextcord.Intents.all()
prefix='!'
bot=commands.Bot(intents=intents)

#bot settings
settings=cluster[os.getenv("main")]["settings"]
TOKEN=settings.find_one({"_id": "main"})["TOKEN"]
DEVS_ID=settings.find_one({"_id": "main"})["DEVS_ID"]
ADMIN_PERSONS_ID=settings.find_one({"_id": "main"})["ADMIN_PERSONS_ID"]
LMAO_CHANNEL_ID=settings.find_one({"_id":"lmao"})["LMAO_CHANNEL_ID"]
GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_all()

# COGS STUFF 

#load all cogs on startup
async def load_all():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            print(f'cogs.{file[:-3]}')
            bot.load_extension(f'cogs.{file[:-3]}')
    print("Loaded all cogs")
    await bot.sync_all_application_commands()

#command to reload all cogs
@bot.slash_command(name="reload_cogs", description="Reload all cogs", guild_ids=GUILD_IDS)
async def reload_cogs(interaction : nextcord.Interaction):
    if interaction.user.id in DEVS_ID:
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    bot.reload_extension(f'cogs.{file[:-3]}')
                except Exception as e:
                    bot.load_extension(f'cogs.{file[:-3]}')
        await bot.sync_all_application_commands()
        await interaction.response.send_message("Reloaded all cogs", ephemeral=True)




bot.run(TOKEN)