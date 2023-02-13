import nextcord
from nextcord.ext import commands
import pymongo
import os
from dotenv import load_dotenv

class Status(commands.Cog):
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot):
        self.bot=bot
        self.cluster=pymongo.MongoClient(os.getenv("db"))
        settings=self.cluster[os.getenv("main")]["settings"]
        self.db = self.cluster[os.getenv("board")]
        self.lmao=self.db["lmao_counter"]
        self.ADMIN_PERSONS_ID=settings.find_one({"_id":"main"})["ADMIN_PERSONS_ID"]
        self.DEVS_ID=settings.find_one({"_id":"main"})["DEVS_ID"]
        self.LMAO_ROLE_ID=settings.find_one({"_id":"lmao"})["LMAO_ROLE_ID"]
        self.LMAO_CHANNEL_ID=settings.find_one({"_id":"lmao"})["LMAO_CHANNEL_ID"]     
    
    @nextcord.slash_command(name="set_status", description="sets bot status", guild_ids=GUILD_IDS)
    async def set_status(self, interaction: nextcord.Interaction, status:str):
        if interaction.user.id in self.DEVS_ID:
            await self.bot.change_presence(activity=nextcord.Game(name=status))
            await interaction.response.send_message(f"Set status to %s" % status, ephemeral=True)
        else:
            await interaction.response.send_message(f"You do not have permission to set status",ephemeral=True)


async def setup(bot):
    bot.add_cog(Status(bot))