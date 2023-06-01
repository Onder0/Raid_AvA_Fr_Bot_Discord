from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.management.Model_Rankup import Rankup

ROLES = [
  {"name": "Off-Tank", "value": "off_tank"},
  {"name": "Healer", "value": "healer"},
  {"name": "Grand Arcane", "value": "grand_arcane"},
  {"name": "Arcane", "value": "arcane"},
  {"name": "Souchefer", "value": "souchefer"},
  {"name": "Mande Tenebre", "value": "mande_tenebre"},
  {"name": "Epee Tranchante", "value": "epee_tranchante"},
  {"name": "Brise Royaume", "value": "brise_royaume"},
  {"name": "Chasse Esprit", "value": "chasse_esprit"},
  {"name": "Frost", "value": "frost"},
  {"name": "Fire", "value": "fire"},
  {"name": "Arbalete", "value": "arbalete"},
  {"name": "Scout", "value": "scout"}
]

class Rank(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    Rankup.create_table()

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("Rank.py is ready!")

  @slash_command(name="rankup", description="Ajoute un +1 dans le rôle sélectionné à la personne sélectionnée.")
  async def rankup(self, interaction : Interaction, 
    personne: nextcord.Member = SlashOption(description="La personne à rankup.", required=True),
    role: str = SlashOption(description="Le rôle pour lequel elle va être rankup.", required=True, choices=[choice["name"] for choice in ROLES])
  ):
    await interaction.response.defer()

    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /rankup {role} {personne.display_name} .")
    
    if not await verif_guild(interaction) : return
    chan_commandes =  interaction.guild.get_channel(settings.chan_commandes)
    if not await verif_chan(interaction, chan_commandes) : return
    
    role_rankup = None
    for choice in ROLES:
      if choice["name"] == role:
        role_rankup = choice["value"]
        break
    role_normal = nextcord.utils.get(interaction.guild.roles, id = getattr(settings, role_rankup))
    role_rankup_op = f"{role_rankup}_op"
    role_op = nextcord.utils.get(interaction.guild.roles, id = getattr(settings, role_rankup_op))

    result_rankup, created = Rankup.get_or_create(id_membre = personne.id)
    setattr(result_rankup, 'nom_membre', personne.display_name)
    
    plus_un = getattr(result_rankup, role_rankup)

    message = ""
    embed = ""
    message_commande = ""
    embed_commande = ""

    if plus_un == 5 :
        message += f":star2: {personne.mention} est déjà {role_op.mention} ! :star2:\n"
        embed = embed_warning("",message)
        embed_commande = embed_success("",message)
        logger.info(f"+ {personne.display_name} était déjà {role_op}")
    else :
        plus_un += 1
        setattr(result_rankup, role_rankup, plus_un)
        if plus_un == 5:
            await personne.remove_roles(role_normal)
            await personne.add_roles(role_op)
            message += f"{personne.mention} à atteint le +5, il est maintenant {role_op.mention} !"
            message_commande += f"{role_op.mention} atteint pour {personne.mention}"
            embed = embed_success("", message)
            embed_commande = embed_success("",message_commande)
            logger.info(f"+ {personne.display_name} est maintenant {role_op}")
        else:
            await personne.add_roles(role_normal)
            message += f":star2: {personne.mention} est maintenant {role_normal.mention} +{plus_un} ! :star2:"
            message_commande += f"{role_normal.mention} +{plus_un} pour {personne.mention}"
            embed = embed_success("", message)
            embed_commande = embed_success("",message_commande)
            logger.info(f"+ {personne.display_name} est {role_normal} +{plus_un} .")
    
    result_rankup.save()

    await interaction.followup.send(embed=embed_commande)
    chan_rankup =  interaction.guild.get_channel(settings.chan_rankup)
    await chan_rankup.send(embed=embed)
    await ghostPing(chan_rankup, personne)
    logger.info(f"Succès !\n")


  @slash_command(name="derank", description="Enlève un +1 dans le rôle sélectionné à la personne sélectionnée.")
  async def derank(self, interaction: Interaction,
    personne: nextcord.Member = SlashOption(description="La personne à dérank", required=True),
    role: str = SlashOption(description="Le rôle pour lequel elle va être rankup.", required=True, choices=[choice["name"] for choice in ROLES]),
    raison: str = SlashOption(description="La raison de son dérank.", required=True)
  ):
    await interaction.response.defer()
    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /rankup {role} {personne.display_name} .")
    
    if not await verif_guild(interaction) : return
    chan_commandes =  interaction.guild.get_channel(settings.chan_commandes)
    if not await verif_chan(interaction, chan_commandes) : return
    
    role_rankup = None
    for choice in ROLES:
      if choice["name"] == role:
        role_rankup = choice["value"]
        break
    role_normal = nextcord.utils.get(interaction.guild.roles, id = getattr(settings, role_rankup))

    result_rankup, created = Rankup.get_or_create(id_membre = personne.id)
    setattr(result_rankup, 'nom_membre', personne.display_name)
    
    plus_un = getattr(result_rankup, role_rankup)
    if plus_un == 1 :
        plus_un = 0
    else :
        plus_un -= 1
    setattr(result_rankup, role_rankup, plus_un)
    result_rankup.save()

    message = ""

    if plus_un == 4 :
        role_rankup_op = f"{role_rankup}_op"
        role_op = nextcord.utils.get(interaction.guild.roles, id = getattr(settings, role_rankup_op))
        await personne.remove_roles(role_op)
        message += f"{personne.mention} n'est plus {role_op.mention} !\nIl est revenu à {role_normal.mention} +{plus_un} !"
        logger.info(f"+ {personne.display_name} n'est plus {role_op}. => {role_normal} +{plus_un}.")
    elif plus_un == 0 :
        message += f"{personne.mention} n'est plus rank en {role_normal.mention} !"
        logger.info(f"+ {personne.display_name} n'est plus rank en {role_normal}.")
    else:
        message += f"{personne.mention} est revenu à {role_normal.mention} +{plus_un} !"
        logger.info(f"+ {personne.display_name} est {role_normal} +{plus_un}.")
    message += f"\n`=> {raison}`"
    
    chan_rankup = interaction.guild.get_channel(settings.chan_rankup)
    await chan_rankup.send(embed=embed_error("",message))
    await interaction.followup.send(embed=embed_warning("", message))
    await ghostPing(chan_rankup, personne)
    logger.info(f"Succès !\n")


def setup(bot):
  bot.add_cog(Rank(bot))
