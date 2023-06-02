from utils import *
from config import *
import nextcord
from nextcord.ext import commands
import shutil


logger.info("=================================================================================")
logger.info("================================ Starting bot... ================================")
logger.info("=================================================================================")
logger.warning(f"Environment: {settings.ENV_FOR_DYNACONF}")

if settings.ENV_FOR_DYNACONF == "development":
    shutil.copy("./database/backup_dev.db", "./database/development.db")
if settings.ENV_FOR_DYNACONF == "production":
    shutil.copy("./database/production.db", "./database/backup_prod.db")

bot = commands.Bot(
    command_prefix=settings.command_prefix,
    intents=nextcord.Intents.all(),
    application_id=settings.application_id,
    # guilds=[settings.guild_id]
)

initial_extensions = [
    # "cogs.bank.",
    "cogs.loops.ClearQuotidien",
    "cogs.loops.UpdateRaids",
    "cogs.management.Invitation",
    "cogs.management.Rank",
    "cogs.management.Vouch",
    "cogs.misc.Misc",
    "cogs.raid.Bonus",
    "cogs.raid.MoveAll",
    "cogs.raid.Stream",
    "cogs.sanctions.Deserteur",
    "cogs.sanctions.Sanction",
]


@bot.event
async def on_ready():
    logger.info(f"Database {settings.database} launched")
    await bot.change_presence(activity=nextcord.Game(name="Attend un Raid !"))
    logger.info("Bot is connected to Discord !")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == settings.bot_id or payload.user_id == settings.raid_helper_id:
        return
    # Confirmation d'un payement :
    if payload.emoji.name == "✅" and (
        payload.channel_id == settings.chan_sanction
        or payload.channel_id == settings.chan_deserteur
    ):
        await payement(bot, payload)


if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)


bot.run(settings.token, reconnect=True)
