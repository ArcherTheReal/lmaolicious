import nextcord
from nextcord.ext import commands
import pymongo
import os

class Viewsnaps (commands.Cog):
    cluster=pymongo.MongoClient(os.getenv("db"))
    settings=cluster[os.getenv("main")]["settings"]
    GUILD_IDS=settings.find_one({"_id":"main"})["GUILD_IDS"]
    def __init__(self, bot):
        self.bot=bot
    @nextcord.slash_command(name="calc_viewsnap", guild_ids=GUILD_IDS)
    async def calc_viewsnap(self, interaction : nextcord.Interaction, original_angle_pitch:float, original_angle_yaw:float, new_angle_pitch:float, new_angle_yaw:float):
        angleA=[original_angle_pitch, original_angle_yaw]
        angleB=[new_angle_pitch, new_angle_yaw]


        delta_yaw=abs(float(angleA[1])-float(angleB[1]))
        delta_pitch=abs(float(angleA[0])-float(angleB[0]))

        sens=delta_pitch/0.022
        m_yaw=delta_yaw/delta_pitch*0.022
        await interaction.response.send_message("Sens: "+str(sens)+'\n'+"M_Yaw: "+str(m_yaw),ephemeral=True)

async def setup(bot):
    bot.add_cog(Viewsnaps(bot))
