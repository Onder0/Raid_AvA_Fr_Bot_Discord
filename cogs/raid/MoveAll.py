from utils import *
from config import *
import nextcord
from nextcord import slash_command, Interaction, SlashOption
from nextcord.ext import commands

import asyncio

class MoveAll(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("MoveAll.py is ready!")

  @slash_command(name="moveall", description="Déplace les personnes du channel où vous vous trouver vers celui choisi.")
  async def moveall(self, interaction : Interaction,
    channel: nextcord.VoiceChannel = SlashOption(description="Channel dans lequel vous voulez aller.", required=True)
  ):
    await interaction.response.defer()
    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /moveall {channel}.")
    
    if not await verif_guild(interaction) : return
    chan_commandes =  interaction.guild.get_channel(settings.chan_commandes)
    if not await verif_chan(interaction, chan_commandes) : return
    
    if interaction.user.voice is None:
        error_msg = await interaction.followup.send(embed=embed_error("","Vous devez être connecté à un canal vocal pour utilisé la commande /moveall"))
        logger.warning(f"Échec: {interaction.user.display_name} n'était pas connecté à un vocal.\n")
        await asyncio.sleep(10)
        await error_msg.delete()
        return

    chan_actuel = interaction.user.voice.channel

    if channel == chan_actuel:
        error_msg = await interaction.followup.send(embed=embed_error("","Vous devez sélectionné un channel différent du votre !"))
        logger.warning(f"Échec: {interaction.user.display_name} a essayé de moveall vers le vocal où il se trouve.\n")
        await asyncio.sleep(10)
        await error_msg.delete()
        return
    
    # Récupère le rôle MOR
    role = nextcord.utils.get(interaction.guild.roles, id = settings.bonus)

    # Déplace tous les utilisateurs d'un canal vocal vers un autre
    for member in chan_actuel.members:
        try:
            await member.move_to(channel)
        except Exception as e :
            logger.error(f"{member.display_name} n'a pas pu être move ! => {e}")
    logger.info(f"+ Move entre {chan_actuel} et {channel}.")

    unBonus = ""
    # Vire le MOR de toutes les personnes qui ont été moves
    for member in channel.members:
        if role in member.roles:
            await member.remove_roles(role)
            logger.info(f"+ {role} retiré à {member.display_name}")
            unBonus += f"\n- {member.display_name}, "
    if unBonus :
        unBonus = unBonus[:-2] # Supprime la dernière virgule et l'espace

    if unBonus == "" :
        await interaction.followup.send(embed=embed_success("",f"Le move all a été effectué avec succès !"))
    else :
        await interaction.followup.send(embed=embed_warning("",f"Le bonus a été retiré à {unBonus}.\n**Le move all a été effectué avec succès !**"))

    logger.info(f"Succès !\n")

  
def setup(bot):
    bot.add_cog(MoveAll(bot))
