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
        voucher: nextcord.Member = SlashOption(
            description="La personne qui vouch le nouveau.", required=True
        ),
    ):
        await interaction.response.defer()
        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /vouch {personne.display_name} {voucher.display_name}"
        )

        if not await verif_guild(interaction):
            return
        cat_regles = nextcord.utils.get(interaction.guild.categories, id=settings.cat_regles)
        if not await verif_categorie(interaction, cat_regles):
            return

        if personne.id == voucher.id:
            logger.warning(f"- personne == voucher => {personne.display_name}")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{interaction.user.mention} ... On ne peut pas se vouch soit même !\n=> /vouch {personne.mention} {voucher.mention}",
                )
            )
            logger.info(f"Échec\n")
            return

        result, created = Invits.get_or_create(id_membre=personne.id)

        if not created:
            logger.warning(f"- {personne.display_name} est déjà vouch !")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{personne.mention} est déjà vouch par <@{result.id_voucher}> depuis le `{result.date.strftime('%d/%m/%Y')}` !\n"
                    f"Pour actualiser le vouch {interaction.user.mention} doit effectué la commande /newvouch !",
                )
            )
            logger.info("Échecs\n")
        else:
            setattr(result, "id_voucher", voucher.id)

            result.save()
            logger.info(f"+ Le vouch a bien été ajouté en DB.")

            msg = await interaction.followup.send(
                embed=embed_success(
                    "",
                    f"Le vouch de {personne.mention} par {voucher.mention} a bien été enregistré !",
                )
            )

            await ghostPing(interaction.channel, personne)
            await ghostPing(interaction.channel, voucher)

            logger.info("Succès\n")

    @slash_command(name="newvouch", description="Modifier le vouch d'une personne.")
    async def newvouch(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="Personne qui se fait vouch.", required=True
        ),
        voucher: nextcord.Member = SlashOption(
            description="Personne qui veut vouch.", required=True
        ),
    ):
        await interaction.response.defer()
        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /newvouch {personne.display_name} {voucher.display_name}"
        )

        if not await verif_guild(interaction):
            return
        cat_regles = nextcord.utils.get(interaction.guild.categories, id=settings.cat_regles)
        if not await verif_categorie(interaction, cat_regles):
            return

        if personne.id == voucher.id:
            logger.warning(f"- personne == voucher => {personne.display_name}")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{interaction.user.mention} ... On ne peut pas se vouch soit même !\n=> /vouch {personne.mention} {voucher.mention}",
                )
            )
            logger.info(f"Échec\n")
            return

        result = Invits.get(id_membre=personne.id)
        if result == None:
            logger.warning(f"- {personne.display_name} n'était pas encore vouch.")
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{personne.mention} n'a pas encore été vouch !\n"
                    f"{interaction.user.mention} utilise /vouch à la place !",
                )
            )
            logger.info(f"Échec\n")
            return

        setattr(result, "id_voucher", voucher.id)
        setattr(result, "date", datetime.datetime.now(tz=pytz.timezone("Europe/Paris")))

        result.save()
        logger.info("+ Changements sauvegardés en DB !")

        await interaction.followup.send(
            embed=embed_success(
                "",
                f"Le vouch de {personne.mention} a été remplacé par {voucher.mention} !",
            )
        )

        logger.info(f"Succès\n")

    @slash_command(name="voucher", description="Afficher par qui la personne a été vouch et quand")
    async def voucher(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="La personne recherchée.", required=True
        ),
    ):
        await interaction.response.defer()

        if not await verif_guild(interaction):
            return
        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        try:
            result = Invits.get(id_membre=personne.id)
        except Exception as e:
            logger.warning(
                f"- {personne.display_name} n'a pas de vouch ou a été vouch avant le {settings.premier_vouch} !"
            )
            await interaction.followup.send(
                embed=embed_warning(
                    "",
                    f"{personne.mention} n'est pas vouch ou alors a été vouch avant le `{settings.premier_vouch}`",
                )
            )
            logger.info(f"Échec\n")
            return

        id_voucher = getattr(result, "id_voucher")
        voucher = await interaction.guild.fetch_member(id_voucher)
        date = getattr(result, "date").strftime("%d/%m/%Y")

        logger.info(f"+ {personne.display_name} a été vouch par {voucher.mention} le {date}")
        await interaction.followup.send(
            embed=embed_success(
                "", f"`{date}` {personne.mention} a été vouch par {voucher.mention} !"
            )
        )

        logger.info(f"Succès\n")


def setup(bot):
    bot.add_cog(Vouch(bot))
