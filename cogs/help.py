import nextcord
from nextcord.ext import commands
import pymongo
import os
class Help(commands.Cog):
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot):
        self.bot=bot


    @nextcord.slash_command(name="help", description="help command", guild_ids=GUILD_IDS)
    async def help(self, interaction : nextcord.Interaction, command:str=None):
        await interaction.response.send_message("Help message placeholder", ephemeral=True)


async def setup(bot):
    bot.add_cog(Help(bot))