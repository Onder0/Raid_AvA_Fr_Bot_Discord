from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.sanctions.Model_NoShow import Model_NoShow
from cogs.sanctions.Model_Sanction import Model_Sanctions

class Deserteur(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    Model_NoShow.create

  @commands.Cog.listener()
  async def on_ready(self):
    logger.info("Deserteur.py is ready!")

  @slash_command(name="deserteur", description="Rajoute un déserteur à la personne sélectionnée.")
  async def deserteur(self, interaction: Interaction,
    personne: nextcord.Member = SlashOption(description="Personne qui a déserté.", required=True)
  ):
    await interaction.response.defer()

    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /deserteur {personne.display_name} .")
    
    if not await verif_guild(interaction) : return
    chan_deserteur =  interaction.guild.get_channel(settings.chan_deserteur)
    if not await verif_chan(interaction, chan_deserteur) : return
    
    chan_ticket = interaction.guild.get_channel(settings.chan_ticket)

    deserteur1 = nextcord.utils.get(interaction.guild.roles, id = settings.deserteur1)
    deserteur2 = nextcord.utils.get(interaction.guild.roles, id = settings.deserteur2)
    deserteur3 = nextcord.utils.get(interaction.guild.roles, id = settings.deserteur3)
    raider = nextcord.utils.get(interaction.guild.roles, id = settings.raider)

    result_deserteur, created = Model_NoShow.get_or_create(id_membre = personne.id)
    setattr(result_deserteur, 'nom_membre', personne.display_name)
    count = getattr(result_deserteur, 'no_show_count')
    if count == 3 :
        error_msg = await interaction.followup.send(embed_error(""f"Vous avez effectuer cette commande sur une personne déjà {deserteur3} !"))
        logger.warning(f"Échec: La commande a été exécutée sur une personne déjà deserteur 3 !\n")
        await asyncio.sleep(15)
        await error_msg.delete()
        return
    total = getattr(result_deserteur, 'no_show_total')
    count += 1
    total += 1
    setattr(result_deserteur, 'no_show_count', count)
    setattr(result_deserteur, 'no_show_total', total)

    # Supprime les anciens message mentionnant la personne si il y en a !
    async for message in chan_deserteur.history(limit=None):
        if personne in message.mentions:
            await message.delete()

    message = ""    
    montant = ""
    role = None

    if count == 3 :
        await personne.remove_roles(deserteur2)
        await personne.add_roles(deserteur3)
        await personne.remove_roles(raider)
        montant = "1M"
        role = deserteur3
    else :
        if count == 2 :
            await personne.remove_roles(deserteur1)
            await personne.add_roles(deserteur2)
            montant = "500k"
            role = deserteur2
        elif count == 1 :
            await personne.add_roles(deserteur1)
            montant = "250k"
            role = deserteur1
        
    logger.info(f"+ {personne.display_name} est maintenant {role}.")  
    message += f"{personne.id} est maintenant {role.mention}. Il a déserté {total} fois !\n"
    if count == 3 :
        message += f"=>Il doit payer {montant} ! Il **DOIT** ouvrir un ticket et payer son amende pour avoir à nouveau accès au serveur !\n"
    else :
        message += f" Il doit payer {montant} ! => Ouvrez un ticket pour payer votre amende.\n"
    message += f"=> {chan_ticket.mention}"

    result_deserteur.save()
    await interaction.followup.send(embed=embed_warning("", message))

    Model_Sanctions.create(
        id_membre = personne.id,
        nom_membre = personne.display_name,
        id_auteur = interaction.user.id,
        nom_auteur = interaction.user.display_name,
        raison = f"NoShow {count}",
        montant = montant,
    )
    logger.info(f"+ Ajout dans la DB.")
    logger.info("Succès\n")


  @slash_command(name="desertions", description="Affiche le nombre de désertions total de la personne choisie")
  async def desertions(self, interaction: Interaction,
    personne: nextcord.Member = SlashOption(description="Personne dont on veut voir le nombre de désertions.", required=True)
  ):
    await interaction.response.defer()
    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /desertions {personne.display_name} .")
    
    if not await verif_guild(interaction) : return
    chan_commandes =  interaction.guild.get_channel(settings.chan_commandes)
    if not await verif_chan(interaction, chan_commandes) : return
    
    result_deserteur, created = Model_NoShow.get_or_create(id_membre = personne.id)

    desertions = getattr(result_deserteur, "no_show_total")
    logger.info(f"+ {personne.display_name} a déserté {desertions} fois.")
    await interaction.followup.send(f"{personne.display_name} a déjà déserté {desertions} fois !")

    logger.info("Succès !\n")


async def pardon(user, sanctionne, guild):
  id_raider = settings.raider
  role_ids = settings.deserteur
  deserteur1 = nextcord.utils.get(guild.roles, id = role_ids.get("1"))
  deserteur2 = nextcord.utils.get(guild.roles, id = role_ids.get("2"))
  deserteur3 = nextcord.utils.get(guild.roles, id = role_ids.get("3"))
  raider = nextcord.utils.get(guild.roles, id = id_raider)

  result_deserteur = Model_NoShow.get(id_membre = sanctionne.id)
  setattr(result_deserteur, 'nom_membre', sanctionne.display_name)
  count = getattr(result_deserteur, 'no_show_count')

  setattr(result_deserteur, 'no_show_count', 0)
  setattr(result_deserteur, "dernier_pardon", datetime.datetime.now(tz=pytz.timezone('Europe/Paris')))
  setattr(result_deserteur, "id_auteur_pardon", user.id)
  setattr(result_deserteur, "nom_auteur_pardon", user.display_name)
  result_deserteur.save()
  
  
  if count == 3 : 
      await sanctionne.remove_roles(deserteur3)
      await sanctionne.add_roles(raider)
      logger.info(f"+ {deserteur3} a été enlevé et le {raider} a été ajouté !")
  else :
      if count == 1 : role = deserteur1
      if count == 2 : role = deserteur2
      await sanctionne.remove_roles(role)
      logger.info(f"+ {role} à été enlevé !")

def setup(bot):
  bot.add_cog(Deserteur(bot))
