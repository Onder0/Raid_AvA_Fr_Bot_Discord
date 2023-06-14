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

    @slash_command(name="ping", description="Renvoie la latence du bot.")
    async def ping(self, interaction: Interaction):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(f"{interaction.user.id}: {interaction.user.display_name} execute /ping !")

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        latence = self.bot.latency * 1000

        logger.info(f"+ Latence du bot : {latence:.2f} ms")
        msg = await interaction.followup.send(
            embed=embed_success("", f"La latence du bot est de `{latence:.2f}ms`")
        )
        await asyncio.sleep(10)
        await msg.delete()

        logger.info("Succès\n")

    @slash_command(name="clear", description="Force le clear quotidien")
    async def clear_quotidien(self, interaction: Interaction):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} effectue la commande /clear !"
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        if not await verif_admin(interaction):
            return
        else:
            await clear_quotidien(self)
            await chan_commandes.send(
                embed=embed_warning(
                    "", f"Le clean a bien été effectué par {interaction.user.mention}"
                )
            )
            chan_temp = interaction.guild.get_channel(settings.chan_temp)
            await chan_temp.send(
                embed=embed_warning(
                    "", f"Le clean a bien été effectué par {interaction.user.mention}"
                )
            )
            logger.info(f"Succès: Le /clear a été effectué par {interaction.user.display_name}\n")


def setup(bot):
    bot.add_cog(Misc(bot))
