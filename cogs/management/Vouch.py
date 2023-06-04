from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.management.Model_Invits import Invits


class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        Invits.create_table()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Rank.py is ready!")

    @slash_command(
        name="vouch",
        description="Ajoute en DB qui a Vouch qui !",
    )
    async def vouch(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(description="Le nouveau membre.", required=True),
        voucheur: nextcord.Member = SlashOption(
            description="La personne qui vouch le nouveau.", required=True
        ),
    ):
        await interaction.response.defer()
        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /vouch {personne.display_name} {voucheur.display_name}"
        )

        if not await verif_guild(interaction):
            return
        cat_regles = nextcord.utils.get(interaction.guild.categories, id=settings.cat_regles)
        if not await verif_categorie(interaction, cat_regles):
            return

        if personne.id == voucheur.id:
            logger.warning(f"- personne == voucheur => {personne.display_name}")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{interaction.user.mention} ... On ne peut pas se vouch soit même !\n=> /vouch {personne.mention} {voucheur.mention}",
                )
            )
            logger.info(f"Échec\n")
            return

        Invits.create(id_membre=personne.id, id_voucheur=voucheur.id)
        logger.info(f"+ Le vouch a bien été ajouté en DB.")

        await interaction.followup.send(
            embed=embed_success(
                "",
                f"Le vouch de {personne.mention} par {voucheur.mention} a été enregistré !",
            )
        )

        await ghostPing(interaction.channel, personne)
        await ghostPing(interaction.channel, voucheur)

        logger.info("Succès\n")

    @slash_command(name="voucheur", description="Afficher par qui la personne a été vouch et quand")
    async def voucheur(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="La personne recherchée.", required=True
        ),
    ):
        await interaction.response.defer()
        f"{interaction.user.id}: {interaction.user.display_name} execute la commande /voucheur {personne.display_name}"

        if not await verif_guild(interaction):
            return
        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        try:
            results = Invits.filter(id_membre=personne.id)
        except Exception:
            logger.warning(f"- {personne.display_name} n'a pas de vouch en DB !")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{personne.mention} n'est pas vouch ! Cause possible \n"
                    f"- Il n'a pas encore été vouch.\n"
                    f"- Il a rejoint le serv avant le `10-04-2023`.\n"
                    f"- Il a été vouch avant le `03-06-2023` par quelqu'un ayant quitté le discord.",
                )
            )
            logger.info(f"Échec\n")
            return

        message = ""

        for result in results:
            id_voucheur = getattr(result, "id_voucheur")
            voucheur = await interaction.guild.fetch_member(id_voucheur)
            date = getattr(result, "date").strftime("%d/%m/%Y")
            logger.info(f"+ {personne.display_name} a été vouch par {voucheur.mention} le {date}")
            message += f"\n `{date}` {personne.mention} a été vouch par {voucheur.mention}"

        await interaction.followup.send(embed=embed_success("", message[2:]))

        logger.info(f"Succès\n")


def setup(bot):
    bot.add_cog(Vouch(bot))
