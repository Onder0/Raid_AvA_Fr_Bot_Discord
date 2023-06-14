from utils import *
from config import *
import nextcord
from nextcord.ext import commands, tasks
import shutil
import datetime
import pytz
from cogs.raid.Model_Streamer import Streamer


class ClearQuotidien(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clear_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("ClearQuotidien.py is ready!")

    @tasks.loop(hours=settings.time_loop_clear_quotidien)
    async def clear_loop(self):
        now = datetime.datetime.now(pytz.utc).astimezone(pytz.utc)

        clear_time = datetime.time(hour=settings.time_execution_clear_quotidien - 2)
        next_clear = datetime.datetime.combine(now.date(), clear_time)
        next_clear = pytz.utc.localize(next_clear)
        if next_clear < now:
            next_clear += datetime.timedelta(days=1)

        wait_time = (next_clear - now).total_seconds()
        wait_hours = wait_time // 3600
        wait_minutes = int((wait_time % 3600) // 60)
        if wait_minutes < 10:
            wait_minutes_str = f"0{wait_minutes}"
        else:
            wait_minutes_str = str(wait_minutes)
        print(f"Prochain clear quotidien dans {wait_hours:.0f}h{wait_minutes_str}.\n")

        wait_time = (next_clear - now).total_seconds()

        await asyncio.sleep(wait_time)
        await clear_quotidien(self)

    @clear_loop.before_loop
    async def before_boucle(self):
        await self.bot.wait_until_ready()


async def clear_quotidien(self):
    logger.info("=================================================================================")
    logger.info("================================ Clear Quotidien ================================")
    logger.info("=================================================================================")

    # =========================== #
    # Effectue un backup des logs #
    # =========================== #
    file_handler.doRollover()
    logger.info("=================================================================================")
    logger.info("================================ Clear Quotidien ================================")
    logger.info(
        f"=================================================================================\n"
    )

    # =========================== #
    # Effectue un backup de la DB #
    # =========================== #

    if settings.ENV_FOR_DYNACONF == "production":
        shutil.copy("./database/production.db", "./database/backup_prod.db")
        logger.info(f"Succès: production.db a été backup vers backup_prod.db !\n")

    # ====================================================== #
    # Supprime tous les messages dans le channel 'commandes' #
    # ====================================================== #
    chan_commandes = self.bot.get_channel(settings.chan_commandes)
    logger.info(
        f"Suppression des messages dans {chan_commandes} du serveur {self.bot.guilds[0].name}."
    )

    messages = []
    async for message in chan_commandes.history(limit=None):
        messages.append(message)

    for message in messages:
        if not message.pinned:
            await message.delete()
    logger.info(f"Succès: Commandes supprimées dans {chan_commandes}.\n")
    await chan_commandes.send(
        embed=embed_success("", f"Tous les messages du channel ont été supprimés.")
    )

    # ====================================================== #
    # Supprime tous les messages dans le channel 'commandes' #
    # ====================================================== #
    chan_temp = self.bot.get_channel(settings.chan_temp)
    logger.info(f"Suppression des messages dans {chan_temp} du serveur {self.bot.guilds[0].name}.")

    messages = []
    async for message in chan_temp.history(limit=None):
        messages.append(message)

    for message in messages:
        if not message.pinned:
            await message.delete()
    logger.info(f"Succès: Commandes supprimées dans {chan_temp}.\n")
    await chan_temp.send(
        embed=embed_success("", f"Tous les messages du channel ont été supprimés.")
    )

    # ====================================================================================== #
    # Supprime tous les messages dans le channel 'annonce raid' envoyés par les utilisateurs #
    # ====================================================================================== #
    bot_id = settings.bot_id
    raid_helper_id = settings.raid_helper_id
    chan_raid_bw = self.bot.get_channel(settings.chan_annonces_raids_bw)
    logger.info(
        f"Suppression des messages dans {chan_raid_bw} du serveur {self.bot.guilds[0].name}."
    )

    messages = []
    async for message in chan_raid_bw.history(limit=None, oldest_first=True):
        if message.author.id == raid_helper_id or message.author.id == bot_id:
            break
        messages.append(message)

    for message in messages:
        if not message.pinned:
            await message.delete()
    logger.info(f"Succès: Commandes supprimées dans {chan_raid_bw}.\n")

    chan_raid_fs = self.bot.get_channel(settings.chan_annonces_raids_fs)
    logger.info(
        f"Suppression des messages dans {chan_raid_fs} du serveur {self.bot.guilds[0].name}."
    )

    messages = []
    async for message in chan_raid_fs.history(limit=None, oldest_first=True):
        if message.author.id == raid_helper_id or message.author.id == bot_id:
            break
        messages.append(message)

    for message in messages:
        if not message.pinned:
            await message.delete()
    logger.info(f"Succès: Commandes supprimées dans {chan_raid_fs}.\n")

    # ===================================================================== #
    # Supprime les messages disant que les personnes ont réglé leurs dettes #
    # ===================================================================== #
    chan_deserteur = self.bot.get_channel(settings.chan_deserteur)
    chan_sanction = self.bot.get_channel(settings.chan_sanction)

    logger.info(
        f"Suppression des messages dans {chan_deserteur} du serveur {self.bot.guilds[0].name}."
    )
    async for message in chan_deserteur.history(limit=None):
        # Vérifier si le message contient la chaîne de texte recherchée
        for embed in message.embeds:
            if embed.description and "a réglé ses dettes" in embed.description:
                await message.delete()
    logger.info(f"Succès: Messages de règlement de dettes supprimés dans {chan_deserteur}\n")

    logger.info(
        f"Suppression des messages dans {chan_sanction} du serveur {self.bot.guilds[0].name}."
    )
    async for message in chan_sanction.history(limit=None):
        # Vérifier si le message contient la chaîne de texte recherchée
        for embed in message.embeds:
            if embed.description and "a réglé ses dettes" in embed.description:
                await message.delete()
    logger.info(f"Succès: Messages de règlement de dettes supprimés dans {chan_sanction}\n")

    # ============================================ #
    # Retrait du rôle de streamer à ceux qui l'ont #
    # ============================================ #
    guild = self.bot.guilds[0]
    id_streamer = settings.streamer
    streamer = nextcord.utils.get(guild.roles, id=id_streamer)

    logger.info(f"Suppression des rôles dans {streamer} du serveur {self.bot.guilds[0].name}.")

    logger.info(f"+ Retrait de tous les {streamer}.")
    users = Streamer.select()

    for user in users:
        user_id = int(user.id_membre)
        membre = guild.get_member(user_id)

        if membre:
            await membre.remove_roles(streamer)

    logger.info(f"+ Tous les rôles {streamer} ont été retirés aux membre l'ayant.")

    try:
        Streamer.drop_table()
        Streamer.create_table()
        logger.info(f"+ La table Streamer a été supprimée et recréée.")
    except Exception as e:
        logger.error(f"- La DB n'est pas valide ou la table n'existe pas : {e}")

    logger.info(f"Succès : Les {streamer} ont été supprimés !\n")

    logger.info("=================================================================================")
    logger.info("================================ Reprise du bot =================================")
    logger.info(
        f"=================================================================================\n"
    )


def setup(bot):
    bot.add_cog(ClearQuotidien(bot))
