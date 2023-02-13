import nextcord
from nextcord.ext import commands
from nextcord.ext import application_checks
import datetime
import asyncio
import pymongo
import os
from dotenv import load_dotenv


class Lmao_reset (commands.Cog):
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot:nextcord.Client):
        self.bot=bot
        self.doLoop = True
        self.cluster=pymongo.MongoClient(os.getenv("db"))
        self.settings=self.cluster[os.getenv("main")]["settings"]
        self.db = self.cluster[os.getenv("board")]
        self.lmao=self.db["lmao_counter"]
        self.ADMIN_PERSONS_ID=self.settings.find_one({"_id":"main"})["ADMIN_PERSONS_ID"]
        self.DEVS_ID=self.settings.find_one({"_id":"main"})["DEVS_ID"]
        self.LMAO_ROLE_ID=self.settings.find_one({"_id":"lmao"})["LMAO_ROLE_ID"]
        self.LMAO_CHANNEL_ID=self.settings.find_one({"_id":"lmao"})["LMAO_CHANNEL_ID"]
        self.currentLoop=0
        self.currentTask=0
        self.LAST_LMAO_ROLE_ID=self.settings.find_one({"_id":"lmao"})["LAST_LMAO_ROLE_ID"]
        self.OLD_LAST_MONTH_ID=self.settings.find_one({"_id":"lmao"})["OLD_LAST_MONTH_ID"]
        self.GUILD_IDS=self.settings.find_one({"_id":"main"})["GUILD_IDS"]


    
    @nextcord.slash_command(name="lmao_monthly_reset_start",guild_ids=GUILD_IDS)
    @application_checks.has_permissions()
    async def lmao_monthly_reset_start(self, interaction: nextcord.Interaction):
        self.doLoop=True
        await interaction.response.send_message("Start timer", ephemeral=True)
        
        while self.doLoop:

            #calculate date
            now=datetime.datetime.now()
            future=now+datetime.timedelta(days=31)
            future=future.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            print(future)
            self.currentLoop=asyncio.sleep((future-now+datetime.timedelta(hours=1)).total_seconds())
            print(future-now+datetime.timedelta(hours=1))
            self.currentTask=asyncio.create_task(self.currentLoop)

            #wait
            await self.currentLoop
            
            #grab elements and add them to month review
            cursor = self.lmao.find().sort("count",pymongo.DESCENDING)
            winner=self.lmao.find_one({"_id":0})
            current=self.cluster["lmao_counts"][str(datetime.datetime.now().month)+str(datetime.datetime.now().year)]
            current.drop()
            for x in cursor:
                if int(x['_id']) != 0:

                    current.insert_one(x)
            


            #write message
            channel=self.bot.get_channel(self.LMAO_CHANNEL_ID)

            await channel.send("A month has ended! You know what that means. RESET L")
            winner_name=self.bot.get_user(winner["dc_id"])
            print(winner_name)
            winner_count=winner["count"]
            await channel.send(f"Lets all congratulate <@{winner_name.id}> for reaching {winner_count} lmao count")


            embed=nextcord.Embed(title="#lmao Leaderboard", description="Top 10 users", color=0x0c56e9)
            embed.set_thumbnail(url="https://cdn.nextcordapp.com/emojis/1036401410562076692.webp?size=56&quality=lossless")
            
            #get data for all #10 people
            cursor = self.lmao.find().sort("count",pymongo.DESCENDING)
    
            for x in cursor:
                if int(x['_id']) != 0:
                    user = self.bot.get_user(int(x['_id']))
                    if user:
                        embed.add_field(name=user.name+"#"+user.discriminator, value=x["count"], inline=False)
    
            #add personal score and send embed
            await channel.send(embed=embed)

            #update roles
            guild=self.bot.get_guild(self.GUILD_IDS[0])
            winner_dc=guild.get_member(winner["dc_id"])
            role=guild.get_role(self.LMAO_ROLE_ID)
            role2=guild.get_role(self.LAST_LMAO_ROLE_ID)
            old_id=guild.get_member(self.OLD_LAST_MONTH_ID)
            await winner_dc.remove_roles(role)
            if old_id!=None:
                await old_id.remove_roles(role2)
            await winner_dc.add_roles(role2)

            #delete all old data
            self.lmao.delete_many({"_id":{"$ne":0}})
            self.lmao.update_one({"_id":0},{"$set":{"count":0, "dc_id":0}})
            self.settings.update_one({"_id":"lmao"},{"$set":{"OLD_LAST_MONTH_ID":winner_dc.id}})

    #slash command to stop the monthly reset of lmao count
    @nextcord.slash_command(name="stop_lmao_reset_timer",guild_ids=GUILD_IDS)
    async def stop_lmao_reset_timer(self, interaction : nextcord.Interaction):
        #check if user has permission
        if interaction.user.id in self.DEVS_ID or interaction.user.id in self.ADMIN_PERSONS_ID:

            #cancel the monthly wait
            self.doLoop=False
            self.currentTask.cancel()
            await interaction.response.send_message("Cancelled", ephemeral=True)
        else:
            await interaction.response.send_message("You dont have permission to stop the timer", ephemeral=True)

    @nextcord.slash_command(name="reset_board",guild_ids=GUILD_IDS)
    async def reset_board(self,interaction:nextcord.Interaction):
        if interaction.user.id in self.DEVS_ID:
            cursor = self.lmao.find().sort("count",pymongo.DESCENDING)
            winner=self.lmao.find_one({"_id":0})
            current=self.cluster["lmao_counts"][str(datetime.datetime.now().month)+str(datetime.datetime.now().year)]
            current.drop()
            for x in cursor:
                if int(x['_id']) != 0:

                    current.insert_one(x)


            embed=nextcord.Embed(title="#lmao Leaderboard", description="Top 10 users", color=0x0c56e9)
            embed.set_thumbnail(url="https://cdn.nextcordapp.com/emojis/1036401410562076692.webp?size=56&quality=lossless")
            
            #get data for all #10 people
            cursor = self.lmao.find().sort("count",pymongo.DESCENDING)
    
            for x in cursor:
                if int(x['_id']) != 0:
                    user = self.bot.get_user(int(x['_id']))
                    if user:
                        embed.add_field(name=user.name+"#"+user.discriminator, value=x["count"], inline=False)
    
            #add personal score and send embed

            #update roles
            guild=self.bot.get_guild(self.GUILD_IDS[0])
            winner_dc=guild.get_member(winner["dc_id"])
            role=guild.get_role(self.LMAO_ROLE_ID)
            role2=guild.get_role(self.LAST_LMAO_ROLE_ID)
            old_id=guild.get_member(self.OLD_LAST_MONTH_ID)
            
            await winner_dc.remove_roles(role)
            if old_id!=None:
                await old_id.remove_roles(role2)
            await winner_dc.add_roles(role2)

            #delete all old data
            self.lmao.delete_many({"_id":{"$ne":0}})
            self.lmao.update_one({"_id":0},{"$set":{"count":0, "dc_id":0}})
            self.settings.update_one({"_id":"lmao"},{"$set":{"OLD_LAST_MONTH_ID":winner_dc.id}})
            await interaction.response.send_message("Reset done")

    #slash command to stop the monthly reset of lmao count
    @nextcord.slash_command(name="stop_lmao_reset_timer",guild_ids=GUILD_IDS)
    async def stop_lmao_reset_timer(self, interaction : nextcord.Interaction):
        #check if user has permission
        if interaction.user.id in self.DEVS_ID or interaction.user.id in self.ADMIN_PERSONS_ID:

            #cancel the monthly wait
            self.doLoop=False
            self.currentTask.cancel()
            await interaction.response.send_message("Cancelled", ephemeral=True)
        else:
            await interaction.response.send_message("You dont have permission to stop the timer", ephemeral=True)



async def setup(bot):
    bot.add_cog(Lmao_reset(bot))