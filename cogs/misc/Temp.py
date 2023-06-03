from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
import datetime

from cogs.loops.ClearQuotidien import clear_quotidien


class Temp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Temp.py is ready!")

    @slash_command(name="temp")
    async def temp(self, interaction: Interaction, pseudo1: str, pseudo2: str, date: str):
        await interaction.response.defer()
        if not await verifs(interaction):
            return

        # ========== ========== ========== ========== ========== ========== ========== ========== ========== ========== ========== #
        membre1 = nextcord.utils.find(lambda m: str(m) == pseudo1, interaction.guild.members)
        membre2 = nextcord.utils.find(lambda m: str(m) == pseudo2, interaction.guild.members)

        if membre1 is None or membre2 is None:
            await interaction.followup.send(
                "Impossible de trouver un ou plusieurs membres correspondant aux pseudos donnés."
            )
            logger.warning("- Les deux membre n'ont pas été trouvés !")
            logger.info(f"Échec\n")
            return

        try:
            from cogs.management.Model_Invits import Invits

            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            Invits.create(
                id_membre=membre1.id,
                id_voucher=membre2.id,
                date=date_obj,
            )
            await interaction.followup.send(
                embed=embed_success(
                    "",
                    f"Ajout dans la DB :\n{membre1.mention} vouch par {membre2.mention} le {date}",
                )
            )
        except Exception as e:
            logger.error(f"Échec: {e}\n")
            await interaction.followup.send(embed=embed_error("", f"Échec: {e}"))
        # ========== ========== ========== ========== ========== ========== ========== ========== ========== ========== ========== #
        return

    @slash_command(name="cleartemp")
    async def cleartemp(self, interaction):
        await interaction.response.defer()
        logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute /cleartemp")

        if not await verif_guild(interaction):
            return
        chan_temp = interaction.guild.get_channel(settings.chan_temp)
        if not await verif_chan(interaction, chan_temp):
            return

        messages = []
        async for message in chan_temp.history(limit=None):
            messages.append(message)

        for message in messages:
            if not message.pinned:
                await message.delete()
        logger.info(f"+Commandes supprimées dans {chan_temp}.")
        await chan_temp.send(
            embed=embed_warning(
                "",
                f"{interaction.user.mention} a fait supprimé tout les messages du chan.",
            )
        )
        logger.info(f"Succès\n")


async def verifs(interaction: Interaction):
    logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute /temp")

    chan_temp = interaction.guild.get_channel(settings.chan_temp)
    if not interaction.user.id in settings.temp_user and await verif_chan(interaction, chan_temp):
        msg = await interaction.followup.send(
            embed=embed_error(
                "",
                f"Vous devez vous trouvez dans {chan_temp.mention} ou être autorisé pour utiliser cette commande !",
            )
        )
        await asyncio.sleep(10)
        msg.delete()
        return False
    return True


def setup(bot):
    bot.add_cog(Temp(bot))
