import nextcord
from nextcord.ext import commands
import pymongo
import os
from dotenv import load_dotenv

class Dev_stuff (commands.Cog):
    
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

    GUILD_IDS=[1043568926614880346, 1004897099017637979]
    @nextcord.slash_command(name="speak", guild_ids=GUILD_IDS)
    async def ping(self, interaction : nextcord.Interaction, message:str):
        if interaction.user.id in self.DEVS_ID:
            await interaction.channel.send(str(message))
            await interaction.response.send_message("Done", ephemeral=True)
        else:
            await interaction.response.send_message("Sry this is a dev command", ephemeral=True)

async def setup(bot):
    bot.add_cog(Dev_stuff(bot))