import nextcord
from nextcord.ext import commands

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    GUILD_IDS=[1043568926614880346, 1004897099017637979]

    @nextcord.slash_command(name="help", description="help command", guild_ids=GUILD_IDS)
    async def help(self, interaction : nextcord.Interaction, command:str=None):
        await interaction.response.send_message("Help message placeholder", ephemeral=True)


async def setup(bot):
    bot.add_cog(Help(bot))