import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from config import settings
from config.logger import logger
import asyncio

async def verification(interaction, personne, verif_role):
    await interaction.response.defer()

    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /{verif_role} {personne.display_name}")
    
    # Envoie un message d'erreur si la guilde n'est pas whitelist 
    if interaction.guild.id is not settings.guild_id:
        error_msg = await interaction.response.send_message("```diff\n- Échec```Votre serveur n'est pas autorisé à utiliser ce bot !")
        logger.warning(f"Échec: Le serveur n'était pas autorisé=> id = {interaction.guild_id}.")
        logger.warning(f"=> nom : {interaction.guild.name} / id : {interaction.guild.id}\n")
        await asyncio.sleep(60)
        await error_msg.delete()
        return
    
    membre = nextcord.utils.get(interaction.guild.roles, id = settings.membre)

    try:
        if verif_role == "membre":
            await personne.add_roles(membre)
            await interaction.followup.send(f"{personne.mention} est maintenant {membre}")
        else :
            raider = nextcord.utils.get(interaction.guild.roles, id = settings.raider)
            await personne.remove_roles(membre)
            await personne.add_roles(raider)
            await interaction.followup.send(f"{personne.mention} est maintenant {raider}")
        logger.info("Succès\n")
    except Exception as e:
        logger.error(f"Échec: {e}")


class Verif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Verif.py is ready!")

    @slash_command(name="membre", description="Ajoute le rôle membre.")
    async def membre(Self,
      interaction: Interaction, 
      personne: nextcord.Member = SlashOption(description="Personne à passer membre.", required=True),
    ):
      await verification(interaction, personne, "membre")

    @slash_command(name="raider", description="Ajoute le rôle raider et enlève membre si besoin.")
    async def raider(self,
      interaction: Interaction,
      personne: nextcord.Member = SlashOption(description="Personne à passer raider.", required=True),
    ):
      await verification(interaction, personne, "raider")

def setup(bot):
    bot.add_cog(Verif(bot))