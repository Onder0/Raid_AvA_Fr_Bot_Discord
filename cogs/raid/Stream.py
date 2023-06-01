from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.raid.Model_Streamer import Streamer


class Stream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        Streamer.create_table()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Stream.py is ready!")

    @slash_command(
        name="stream", description="Permet à une personne de streamer dans les canaux de raids !"
    )
    async def stream(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="La personne qui pourra streamer.", required=True
        ),
    ):
        await interaction.response.defer()
        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} exécute la commande /stream {personne.display_name} ."
        )

        if not await verif_guild(interaction):
            return
        chan_commande = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commande):
            return

        streamer = nextcord.utils.get(interaction.guild.roles, id=settings.streamer)

        await personne.add_roles(streamer)
        await interaction.followup.send(
            embed=embed_success("", f"{personne.mention} est {streamer.mention} jusqu'à 6h !")
        )
        logger.info(f"+ {streamer} ajouté à {personne.display_name}")

        # Ajout du membre dans la DB Streamer
        result_streamer, created = Streamer.get_or_create(id_membre=personne.id)
        setattr(result_streamer, "nom_membre", personne.display_name)
        result_streamer.save()
        logger.info(f"+ Ajout de {personne.display_name} dans la DB Streamer")

        logger.info("Succès\n")


def setup(bot):
    bot.add_cog(Stream(bot))
