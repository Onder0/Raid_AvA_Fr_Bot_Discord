import nextcord
from nextcord.ext import commands
from config import settings
from config.logger import logger

logger.info("=====================================")
logger.info("========== Starting bot... ==========")
logger.info("=====================================")
logger.info(f"Environment: {settings.ENV_FOR_DYNACONF}")

if settings.ENV_FOR_DYNACONF == "DEVELOPMENT":  
  import shutil
  shutil.copy("./database/backup.db", "./database/development.db")

bot = commands.Bot(
  command_prefix=settings.command_prefix,
  intents=nextcord.Intents.all(),
  application_id=settings.guild_id
  #guilds=[settings.guild]
)

initial_extensions = [
  "cogs.ping.Ping",
]

@bot.event
async def on_ready():
  logger.info(f"Database {settings.database} launched")
  logger.info("Bot is connected to Discord")


if __name__ == '__main__':
  for extension in initial_extensions:
    bot.load_extension(extension)


bot.run(settings.token, reconnect=True)