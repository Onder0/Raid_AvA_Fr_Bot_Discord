from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands

class Misc(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("Misc.py is ready!")

  

def setup(bot):
  bot.add_cog(Misc(bot))
