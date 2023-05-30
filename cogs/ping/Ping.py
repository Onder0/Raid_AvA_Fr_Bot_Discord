from nextcord import slash_command, Interaction
from nextcord.ext import commands
from config import settings
from config.logger import logger
import asyncio

class Ping(commands.Cog,):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Ping.py is ready!\n")

    @slash_command(name="ping", description="retourne la latence du bot.")
    async def ping(self, 
                   interaction: Interaction
                   ):
        await interaction.response.defer()
        
        logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute la commande /ping.")

        # Envoie un message d'erreur si la guilde n'est pas whitelist 
        if interaction.guild.id is not settings.guild_id:
            error_msg = await interaction.response.send_message("```diff\n- Échec```Votre serveur n'est pas autorisé à utiliser ce bot !")
            logger.warning(f"Échec: Le serveur n'était pas autorisé=> id = {interaction.guild_id}.")
            logger.warning(f"=> nom : {interaction.guild.name} / id : {interaction.guild.id}\n")
            await asyncio.sleep(60)
            await error_msg.delete()
            return
        
        # Récupère le chan texte Commandes
        chan_commandes =  settings.chan_commandes
        # Si le message n'est pas dans commandes, afficher une erreur
        if (interaction.channel != chan_commandes) :
            error_msg = await interaction.followup.send(f"```diff\n- Échec```Vous devez effectuer cette commande dans le channel {chan_commandes.mention} !")
            logger.warning(f"Échec: La commande a été exécutée dans {interaction.channel} au lieu de {chan_commandes} !\n")
            await asyncio.sleep(15)
            await error_msg.delete()
            return

        msg = await interaction.followup.send(f'Mon ping est de {self.bot.latency}!')
        logger.info(f"Ping : {self.latency}.\n")
        await asyncio.sleep(15)
        await msg.delete()


def setup(bot):
    bot.add_cog(Ping(bot))
