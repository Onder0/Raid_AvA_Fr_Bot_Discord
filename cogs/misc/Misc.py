from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands

from cogs.loops.ClearQuotidien import clear_quotidien


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Misc.py is ready!")

    @nextcord.slash_command(name="clear", description="Force le clear quotidien")
    async def clear_quotidien(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        logger.info(f"{interaction.user.display_name} effectue la commande /clear !")

        if not await verif_guild(interaction):
            return
        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        admin_id = settings.admin
        roles_requis = [admin_id]
        user_roles = [role.id for role in interaction.user.roles]
        # Vérifie que la personne peut faire le payement
        a_role_requis = any(role_id in user_roles for role_id in roles_requis)
        if not a_role_requis:
            admin = interaction.guild.get_role(admin_id)
            error_msg = await interaction.followup.send(
                embed=embed_error(
                    "", f"Vous devez être {admin.mention} pour effectué la commande !"
                )
            )
            logger.warning(f"Échec: La commande a été exécutée dans {interaction.channel} !\n")
            await asyncio.sleep(10)
            await error_msg.delete()
        else:
            await clear_quotidien(self)
            await chan_commandes.send(
                embed=embed_warning(
                    "", f"Le clean a bien été effectué par {interaction.user.mention}"
                )
            )
            logger.info(f"Succès: Le /clear a été effectué par {interaction.user.display_name}\n")


def setup(bot):
    bot.add_cog(Misc(bot))
