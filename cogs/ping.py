import nextcord
from nextcord.ext import commands

class Ping (commands.Cog):
    
    def __init__(self, bot):
        self.bot=bot
    GUILD_IDS=[1043568926614880346, 1004897099017637979]
    @nextcord.slash_command(name="ping", guild_ids=GUILD_IDS)
    async def ping(self, interaction : nextcord.Interaction):
        await interaction.response.send_message("Pong", ephemeral=True)

async def setup(bot):
    bot.add_cog(Ping(bot))