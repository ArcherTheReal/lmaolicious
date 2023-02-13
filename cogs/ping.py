import nextcord
from nextcord.ext import commands
import pymongo
import os
class Ping (commands.Cog):
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot):
        self.bot=bot
    @nextcord.slash_command(name="ping", guild_ids=GUILD_IDS)
    async def ping(self, interaction : nextcord.Interaction):
        await interaction.response.send_message("Pong", ephemeral=True)

async def setup(bot):
    bot.add_cog(Ping(bot))