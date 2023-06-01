from utils import *
from config import *
import nextcord
from nextcord.ext import commands, tasks
from cogs.raid.Model_Streamer import Streamer

class ClearQuotidien(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.clear_loop.start()
    

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("ClearQuotidien.py is ready!")

  @nextcord.slash_command(name="clear", description="Force le clear quotidien")
  async def clear_quotidien(self, interaction : nextcord.Interaction):
    await interaction.response.defer()
    logger.info(f"{interaction.user.display_name} effectue la commande /clear !")

    if not await verif_guild(interaction) : return
    chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
    if not await verif_chan(interaction, chan_commandes) : return

    admin_id = settings.admin
    modo_id = settings.modo
    roles_requis = [admin_id, modo_id]
    user_roles = [role.id for role in interaction.user.roles]
    # Vérifie que la personne peut faire le payement
    a_role_requis = any(role_id in user_roles for role_id in roles_requis)
    if not a_role_requis:
      admin = interaction.guild.get_role(admin_id)
      modo = interaction.guild.get_role(modo_id)
      error_msg = await interaction.followup.send(embed=embed_error("",
								f"Vous devez être {admin.mention} ou {modo.mention} pour effectué la commande !"))
      logger.warning(f"Échec: La commande a été exécutée dans {interaction.channel} !\n")
      await asyncio.sleep(10)
      await error_msg.delete()
    else :
      await clear_quotidien(self)
      await chan_commandes.send(embed=embed_warning("", f"Le clean a bien été effectué par {interaction.user.mention}"))
  

  @tasks.loop(hours=24)
  async def clear_loop(self):
    
    now = datetime.datetime.now(pytz.utc)

    clear_time = datetime.time(hour=4, minute=0)
    next_clear = datetime.datetime.combine(now.date(), clear_time)
    if next_clear < now:
        next_clear += datetime.timedelta(days=1)

    wait_time = (next_clear - now).total_seconds()

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
    for embed in message.embeds:
      if embed.description and "a réglé ses dettes" in embed.description:
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
  users = Streamer.select()

  for user in users:
      user_id = int(user.id_membre)
      membre = guild.get_member(user_id)

      if membre :
          await membre.remove_roles(streamer)

  logger.info(f"+ Tous les rôles {streamer} ont été retirés aux membre l'ayant.")

  try :
      Streamer.drop_table()
      Streamer.create_table()
      logger.info(f"La table Streamer a été supprimée et recréée.")
  except Exception as e :
      logger.warning(f"La DB n'est pas valide ou la table n'existe pas : {e}")



def setup(bot):
  bot.add_cog(ClearQuotidien(bot))
