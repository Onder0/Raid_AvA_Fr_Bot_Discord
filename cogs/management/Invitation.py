from utils import *
from config import *
import nextcord
from nextcord import slash_command, Interaction, SlashOption
from nextcord.ext import commands


class Invitation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Verif.py is ready!")

    @slash_command(name="membre", description="Ajoute le rôle membre.")
    async def membre(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="Personne à passer membre.", required=True
        ),
    ):
        await verification(interaction, personne, "membre")

    @slash_command(name="raider", description="Ajoute le rôle raider et enlève membre si besoin.")
    async def raider(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="Personne à passer raider.", required=True
        ),
    ):
        await verification(interaction, personne, "raider")


async def verification(interaction, personne: nextcord.Member, verif_role):
    await interaction.response.defer()
    logger.info(
        f"{interaction.user.id}: {interaction.user.display_name} execute la commande /{verif_role} {personne.display_name}"
    )

    if not await verif_guild(interaction):
        return
    cat_regles = nextcord.utils.get(interaction.guild.categories, id=settings.cat_regles)
    cat_tickets = nextcord.utils.get(interaction.guild.categories, id=settings.cat_tickets)
    if not await verif_categorie(interaction, cat_regles) or not await verif_categorie(
        interaction, cat_tickets
    ):
        return

    membre = nextcord.utils.get(interaction.guild.roles, id=settings.membre)

    try:
        if verif_role == "membre":
            await personne.add_roles(membre)
            await interaction.followup.send(
                embed=embed_success("", f"{personne.mention} est maintenant {membre.mention}")
            )
        else:
            raider = nextcord.utils.get(interaction.guild.roles, id=settings.raider)
            await personne.remove_roles(membre)
            await personne.add_roles(raider)
            await interaction.followup.send(
                embed=embed_success("", f"{personne.mention} est maintenant {raider.mention}")
            )
        logger.info("Succès\n")
        await ghostPing(interaction.channel, personne)
    except Exception as e:
        logger.error(f"Échec: {e}")


def setup(bot):
    bot.add_cog(Invitation(bot))
