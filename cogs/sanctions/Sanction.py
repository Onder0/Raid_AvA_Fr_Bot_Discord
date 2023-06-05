from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.sanctions.Model_Sanction import Sanctions


class Sanction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        Sanctions.create_table()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Sanction.py is ready!\n")

    @slash_command(name="sanction", description="Ajoute une sanction à la personne sélectionnée.")
    async def sanction(
        self, interaction: Interaction, personne: nextcord.Member, sanction: str, montant: str
    ):
        await interaction.response.defer()
        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /sanction {personne.display_name} ."
        )

        if not await verif_guild(interaction):
            return
        chan_sanction = interaction.guild.get_channel(settings.chan_sanction)
        if not await verif_chan(interaction, chan_sanction):
            return

        chan_ticket = interaction.guild.get_channel(settings.chan_ticket)

        Sanctions.create(
            id_membre=personne.id,
            nom_membre=personne.display_name,
            id_auteur=interaction.user.id,
            nom_auteur=interaction.user.display_name,
            raison=sanction,
            montant=montant,
        )
        role = nextcord.utils.get(interaction.guild.roles, id=settings.sanctionne)
        await personne.add_roles(role)
        logger.info(f"+ La sanction et le rôle ont bien été ajoutés.")

        await interaction.followup.send(
            embed=embed_error(
                "",
                f"{personne.mention}, tu as été sanctionné pour `{sanction}`\n"
                f"Tu dois payer `{montant} silvers` au discord => {chan_ticket.mention} !",
            )
        )
        await ghostPing(chan_sanction, personne)
        logger.info("Succès !\n")


def setup(bot):
    bot.add_cog(Sanction(bot))
