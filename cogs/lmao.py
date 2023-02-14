import nextcord
from nextcord.ext import commands
import pymongo
import os
from dotenv import load_dotenv



class Lmao (commands.Cog):
    
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot):
        self.bot=bot
        self.cluster=pymongo.MongoClient(os.getenv("db"))
        self.settings=self.cluster[os.getenv("main")]["settings"]
        self.db = self.cluster[os.getenv("board")]
        self.lmao=self.db["lmao_counter"]
        self.ADMIN_PERSONS_ID=self.settings.find_one({"_id":"main"})["ADMIN_PERSONS_ID"]
        self.DEVS_ID=self.settings.find_one({"_id":"main"})["DEVS_ID"]
        self.LMAO_ROLE_ID=self.settings.find_one({"_id":"lmao"})["LMAO_ROLE_ID"]
        self.LMAO_CHANNEL_ID=self.settings.find_one({"_id":"lmao"})["LMAO_CHANNEL_ID"]
        self.LOCKED=False
    #------- STUFF --------


    #embed for lmao board
    @nextcord.slash_command(name="lmaoboard", description="Displays the top 10 LMAOers", guild_ids=GUILD_IDS)
    async def lmaoboard(self, interaction : nextcord.Interaction, year : int=None,month : int=None):
        if year is None or month is None:
            

            #make embed
            embed=nextcord.Embed(title="#lmao Leaderboard", description="Top 10 users", color=0x0c56e9)
            embed.set_thumbnail(url="https://sp-ao.shortpixel.ai/client/to_webp,q_glossy,ret_img,w_128,h_126/https://getonstream.com/wp-content/uploads/2021/06/0cd.png")

            #get data for all #10 people
            cursor = self.lmao.find().sort("count",pymongo.DESCENDING).limit(10)
            length=0
            for x in cursor:
                if int(x['_id']) != 0:
                    length+=1
                    user = self.bot.get_user(int(x['_id']))
                    if user:
                        embed.add_field(name=user.name+"#"+user.discriminator, value=x["count"], inline=False)


            #get personal score
            if (length>1):
                score = self.lmao.find_one({"_id":int(interaction.user.id)})["count"]
            else:
                score=None

            #add personal score and send embed
            if score is not None:       
                embed.set_footer(text="Your score: "+str(score))
            else:
                embed.set_footer(text="You dont have a score yet")
            await interaction.response.send_message(embed=embed)

        else:
            archive=self.cluster.lmao_counts[f"{month}{year}"]
            if archive is None:
                await interaction.response.send_message("Archive cannot be found")
            else:

                #make embed
                embed=nextcord.Embed(title=f"#lmao Leaderboard of month {month}, year {year}", description="Top 10 users of given month", color=0x0c56e9)
                embed.set_thumbnail(url="https://sp-ao.shortpixel.ai/client/to_webp,q_glossy,ret_img,w_128,h_126/https://getonstream.com/wp-content/uploads/2021/06/0cd.png")

                #get data for all #10 people
                cursor = archive.find().sort("count",pymongo.DESCENDING).limit(10)

                length=0
                for x in cursor:
                    length+=1
                    if int(x['_id']) != 0:
                        user = self.bot.get_user(int(x['_id']))
                        if user:
                            embed.add_field(name=user.name+"#"+user.discriminator, value=x["count"], inline=False)
                await interaction.response.send_message(embed=embed)


    #command to set lmao count
    @nextcord.slash_command(name="set_lmao",description="Sets someones lmao", guild_ids=GUILD_IDS)
    async def set_lmao(self, interaction : nextcord.Interaction,user : nextcord.Member, number : int):
        #check if we have permission
        if (interaction.user.id in self.DEVS_ID or interaction.user.id in self.ADMIN_PERSONS_ID):
            #find person mentioned
            cursor=self.lmao.find_one({"_id":user.id})
            if (cursor!=None):
                if (number>=0):
                    if (number%1==0):
                        #set lmao count
                        self.lmao.update_one({"_id":user.id},{"$set":{"count":number}})
                        name=str(user.name)
                        num=str(number)
                        await interaction.response.send_message(f"Set {name}'s lmao count to {num}", ephemeral=True)
                    else:
                        await interaction.response.send_message("Error: number must be a whole number", ephemeral=True)
                else:
                    await interaction.response.send_message("Error: number must be non negativ", ephemeral=True)
            else:
                await interaction.response.send_message("Error: this user does not have an lmao count", ephemeral=True)
        else:
            await interaction.response.send_message("Error: you dont have permission to use this command", ephemeral=True)
    
    #command to get lmao count
    @nextcord.slash_command(name="get_lmao",description="Get Someones lmao count", guild_ids=GUILD_IDS)
    async def get_lmao(self,interaction : nextcord.Interaction, user : nextcord.Member):
        #find person mentioned
        result=self.lmao.find_one({"_id":user.id})
        #check if person lmao count exists
        if result!=None:
            num=result["count"]
            await interaction.response.send_message(f"The lmao count of {user.name} is  {num}", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.name} does not have an lmao count", ephemeral=True)

    @nextcord.slash_command(name="lock_board", guild_ids=GUILD_IDS)
    async def lock_board(self,interaction : nextcord.Interaction, state:bool):
        if (interaction.user.id in self.DEVS_ID):
            self.LOCKED=state
            await interaction.response.send_message("Changed leaderboard to {state}")
        else:
            await interaction.response.send_message("What did you think dummy?\n Only devs can use this command")

    #listener to receive lmao messages
    @commands.Cog.listener()
    async def on_message(self, ctx : nextcord.Message):
        #check if message in #lmao and message startswith "lmao"demo
        if self.LOCKED==False and int(ctx.channel.id)==self.LMAO_CHANNEL_ID and str(ctx.content).lower().startswith("lmao"):
            #get person
            result=self.lmao.find_one({"_id":int(ctx.author.id)})
            #if person exists
            if result!=None:
                #set new lmao count
                self.lmao.update_one(
                    { "_id": int(ctx.author.id) },
                    { "$inc": {"count":1} })
                await ctx.add_reaction("✅")
                #get stuff to see if new record
                result=self.lmao.find_one({"_id":int(ctx.author.id)})
                maxed=self.lmao.find_one({"_id":0})
                current_count=result["count"]
                maxed_count=maxed["count"]
                #check if new record
                if current_count>maxed_count:
                    #update record
                    guild = ctx.guild
                    old=guild.get_member(maxed["dc_id"])
                    new=guild.get_member(int(ctx.author.id))
                    role=guild.get_role(self.LMAO_ROLE_ID)
                    #handle roles
                    if old!=None:
                        await old.remove_roles(role)
                    await new.add_roles(role)
                    self.lmao.update_one({"_id":0},{"$set":{"dc_id":int(ctx.author.id),"count":current_count}})


            else:
                self.lmao.insert_one({"_id":int(ctx.author.id),"count":1})



async def setup(bot):
   bot.add_cog(Lmao(bot))
