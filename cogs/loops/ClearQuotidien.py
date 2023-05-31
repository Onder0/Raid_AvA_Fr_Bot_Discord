from utils import *
from config import *
import nextcord
from nextcord.ext import commands, tasks
from cogs.raid.Model_Streamer import Model_Streamer

class ClearQuotidien(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.clear_loop.start()
    

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("ClearQuotidien.py is ready!")

  @nextcord.slash_command(name="clear", description="Force le clear quotidien")
  async def clear_quotidien(self, interaction : nextcord.Interaction):
     await clear_quotidien(self)
     await interaction.channel.send(embed=embed_success("","Le clear quotidien à bien été effectué"))
  

  @tasks.loop(hours=24)
  async def clear_loop(self):

    clear_time = datetime.time(hour=4, minute=0)
    next_clear = datetime.datetime.combine(datetime.now.date(), clear_time)
    if next_clear < datetime.now:
        next_clear += datetime.timedelta(days=1)

    wait_time = (next_clear - datetime.now).total_seconds()

    # wait_hours = wait_time // 3600
    # wait_minutes = int((wait_time % 3600) // 60)
    # if wait_minutes < 10:
    #     wait_minutes_str = f"0{wait_minutes}"
    # else:
    #     wait_minutes_str = str(wait_minutes)
    # logger.info(f"Prochain clean du chan commandes dans {wait_hours:.0f}h{wait_minutes_str}.\n")

    await asyncio.sleep(wait_time)
    await clear_quotidien(self)


async def clear_quotidien(self):
  logger.info("=================================================================================")
  logger.info("================================ Clear Quotidien ================================")
  logger.info("=================================================================================")

  # =========================== #
  # Effectue un backup des logs #
  # =========================== #
  file_handler.doRollover()
  logger.info(f"Le logs ont été backup !")

  # ====================================================== #
  # Supprime tous les messages dans le channel 'commandes' #
  # ====================================================== #
  chan_commandes = self.bot.get_channel(settings.chan_commandes)
  logger.info(f"Suppression des messages dans {chan_commandes} du serveur {self.bot.guilds[0].name}.")
  
  messages = []
  async for message in chan_commandes.history(limit=None):
      messages.append(message)
  
  for message in messages:
      if not message.pinned:
          await message.delete()
  logger.info(f"Succès: Commandes supprimées dans {chan_commandes}.")
  await chan_commandes.send(embed=embed_success("",f"Tous les messages du channel ont été supprimés."))

  # ====================================================================================== #
  # Supprime tous les messages dans le channel 'annonce raid' envoyés par les utilisateurs #
  # ====================================================================================== #
  bot_id = settings.bot_id
  raid_helper_id = settings.raid_helper_id
  chan_raid = self.bot.get_channel(settings.chan_annonces_raids)
  logger.info(f"Suppression des messages dans {chan_raid} du serveur {self.bot.guilds[0].name}.")

  messages = []
  async for message in chan_raid.history(limit=None):
    if message.author.id == raid_helper_id or message.author.id == bot_id :
        break
    messages.append(message)
  
  for message in messages:
    if not message.pinned:
        await message.delete()
  logger.info(f"Succès: Commandes supprimées dans {chan_raid}.")
  
  # ===================================================================== #
  # Supprime les messages disant que les personnes ont réglé leurs dettes #
  # ===================================================================== #
  chan_deserteur = self.bot.get_channel(settings.chan_deserteur)
  chan_sanction = self.bot.get_channel(settings.chan_sanction)

  logger.info(f"Suppression des messages dans {chan_deserteur} du serveur {self.bot.guilds[0].name}.")
  async for message in chan_deserteur.history(limit=None):
    # Vérifier si le message contient la chaîne de texte recherchée
    for embed in message.embeds:
      if embed.description and "a réglé ses dettes" in embed.description:
        await message.delete()
  logger.info(f"Succès : Messages de règlement de dettes supprimés dans {chan_deserteur}")

  logger.info(f"Suppression des messages dans {chan_sanction} du serveur {self.bot.guilds[0].name}.")
  async for message in chan_sanction.history(limit=None):
    # Vérifier si le message contient la chaîne de texte recherchée
    if "a réglé ses dettes" in message.content:
        await message.delete()
  logger.info(f"Succès : Messages de règlement de dettes supprimés dans {chan_sanction}")

  # ============================================ #
  # Retrait du rôle de streamer à ceux qui l'ont #
  # ============================================ #
  guild = self.bot.guilds[0]
  id_streamer = settings.streamer
  streamer = nextcord.utils.get(guild.roles, id = id_streamer)

  logger.info(f"Suppression des rôles dans {streamer} du serveur {self.bot.guilds[0].name}.")
  
  logger.info(f"+ Retrait de tous les {streamer}.")
  users = Model_Streamer.select()

  for user in users:
      user_id = int(user.id_membre)
      membre = guild.get_member(user_id)

      if membre :
          await membre.remove_roles(streamer)

  logger.info(f"+ Tous les rôles {streamer} ont été retirés aux membre l'ayant.")

  try :
      Model_Streamer.drop_table()
      Model_Streamer.create_table()
      logger.info(f"La table Streamer a été supprimée et recréée.")
  except Exception as e :
      logger.warning(f"La DB n'est pas valide ou la table n'existe pas : {e}")



def setup(bot):
  bot.add_cog(ClearQuotidien(bot))
