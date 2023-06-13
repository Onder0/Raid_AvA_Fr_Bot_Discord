from utils import *
from config import *
import nextcord
import requests
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from datetime import datetime


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Presence.py is ready!")

    @slash_command(
        name="presence", description="Retourne les membres manquant et les membres s'étant rajouté"
    )
    async def presence(self, interaction: Interaction):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /presence !"
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return
        voc_attente_raid = interaction.guild.get_channel(settings.voc_attente_bonus)
        if not voc_attente_raid.states:
            error_msg = await interaction.followup.send(
                embed=embed_error("", f"Il n'y a personne dans {voc_attente_raid.mention} !")
            )
            logger.warning(f"- Il n'y a personne dans {voc_attente_raid.mention} !")
            await asyncio.sleep(10)
            await error_msg.delete()
            logger.info(f"Échec\n")

        user_id = settings.raid_helper_id
        api_key = settings.raid_helper_token
        chan_annonces_raids = interaction.guild.get_channel(settings.chan_annonces_raids)

        inscritsIds = []
        absentPresentIds = []
        rawVocalIds = []

        logger.info("+ Récupération des Ids !")

        # ===== récup joueurs inscrits ===== #
        messages = await chan_annonces_raids.history(limit=None).flatten()
        import re

        user_messages = [message for message in messages if message.author.id == user_id]

        now = datetime.now()

        closest_event = None
        closest_event_time = float("inf")  # Valeur initiale pour représenter l'infini

        for user_message in user_messages:
            if user_message.embeds:
                embed = user_message.embeds[0]
                for field in embed.fields:
                    value = field.value
                    match = re.search(r"<t:(\d+):", value)
                    if match:
                        timestamp = int(match.group(1))
                        event_time = datetime.fromtimestamp(timestamp)
                        time_difference = event_time - now

                        if (
                            time_difference.total_seconds() >= 0
                            and time_difference.total_seconds() < closest_event_time
                        ):
                            closest_event = user_message
                            closest_event_time = time_difference.total_seconds()

        if closest_event is None:
            logger.warning("- Aucun événement trouvé.")
            await interaction.followup.send(embed=embed_error("", "Aucun événement trouvé."))
            return

        url = f"https://raid-helper.dev/api/v2/events/{closest_event.id}"
        headers = {"Authorization": api_key}
        response = requests.get(url, headers=headers)

        if response:
            data = response.json()
            signUps = data.get("signUps")
            for signUp in signUps:
                userId = signUp.get("userId")
                if signUp.get("className") != "Absence":
                    inscritsIds.append(f"<@{userId}>")
                else:
                    absentPresentIds.append(f"<@{userId}>")
            logger.info("+ Ids des joueurs inscrits récupérées !")

        else:
            logger.warning(f"- Échec de la connexion à Raid Helper")
            interaction.followup.send(
                embed=embed_error("", f"Échec de la connexion à Raid Helper !")
            )
            return

        # ===== récup joueurs en vocal ===== #

        for member in voc_attente_raid.members:
            rawVocalIds.append(member.id)
        vocalIds = [f"<@{id}>" for id in rawVocalIds]
        logger.info("+ Ids des joueurs en voc récupérées !")

        absentsInscritsIds = set(inscritsIds) - set(vocalIds)
        absentVocalIds = set(vocalIds) - set(inscritsIds) - set(absentPresentIds)

        # ===== Gestion du message ===== #

        msg = ""

        msg = f"**__Joueurs absents :__**\n"
        if len(absentsInscritsIds) > 0:
            for absentsInscritsId in absentsInscritsIds:
                msg += f"- {absentsInscritsId}\n"
        else:
            msg += "**Aucun**\n"

        if len(absentVocalIds) > 0:
            msg += f"\n**__Joueur non inscrits :__**\n"
            for absentVocalId in absentVocalIds:
                msg += f"- {absentVocalId}\n"

        if len(absentPresentIds) > 0:
            msg += f"\n**__Absents présents :__**\n"
            for absentPresentId in absentPresentIds:
                msg += f"- {absentPresentId}\n"

        await interaction.followup.send(embed=embed_success("", msg[:-1]))

        logger.info("Succès\n")
        await logs(interaction, f"execute la commande /presence")


def setup(bot):
    bot.add_cog(Presence(bot))
