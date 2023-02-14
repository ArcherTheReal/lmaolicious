import nextcord
import requests
from nextcord.ext import commands
from nextcord import slash_command
import pymongo
import os
from dotenv import load_dotenv

URL = "https://discordapp.com/api/webhooks/1051582452449169529/C5ImR6R-4anpkTM3Ppighvb7dG7K4Anue2GI47w6qgC2LSOn9-lzuwCHuHTC_yqOJeGj"

PIN_AMOUNT = 4
class Pinnerino(commands.Cog):
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
        self.WOLFBOY248_TM=self.cluster["poggerino"]["used_messages"] # its actually used to store the message that are in use, but wolfboy248 is very funny

    @commands.Cog.listener("on_raw_reaction_add")
    async def reaction_created(self,payload: nextcord.RawReactionActionEvent):
        if payload.event_type == "REACTION_ADD":
            if (payload.emoji.id != None and payload.emoji.id ==1004917381480599622):
                channel = await nextcord.Client.fetch_channel(self.bot,payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                pins = 0
                for reaction in message.reactions:
                    if not isinstance(reaction.emoji, str):
                        if int(reaction.emoji.id) == 1004917381480599622:
                            pins = reaction.count

                if pins >= PIN_AMOUNT:
                    result=self.WOLFBOY248_TM.find_one({"_id":message.id})
                    if result is None:
                        self.WOLFBOY248_TM.insert_one({"_id":message.id})
                        file_text = ""
                        if len(message.attachments) > 0:
                            file_text = "Attachments:\n"
                            for file in message.attachments:
                                file_text = file_text + file.url +"\n"
                        
                        requests.post(url=URL,json={
                            "content":file_text+message.content+"\n",

                            "embeds":[
                                {
                                    "title":"Jump",
                                    "url":message.jump_url
                                }
                            ],
                            "username":message.author.display_name,
                            "avatar_url":message.author.display_avatar.url
                        })

    

async def setup(bot):
    bot.add_cog(Pinnerino(bot))