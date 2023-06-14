from utils import *
from config import *
import nextcord
import requests
from nextcord import slash_command, message_command, Interaction
from nextcord.ext import commands


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Presence.py is ready!")

    @message_command(name="presence")
    async def presence(self, interaction: Interaction, annonce_raid: nextcord.Message):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /presence !"
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)

        voc_attente_raid = interaction.guild.get_channel(settings.voc_attente_raid)
        if not voc_attente_raid.members:
            error_msg = await interaction.followup.send(
                embed=embed_error(
                    "", f"Il n'y a personne dans {voc_attente_raid.mention} !", ephemeral=True
                )
            )
            logger.warning(f"- Il n'y a personne dans {voc_attente_raid.mention} !")
            await asyncio.sleep(5)
            await error_msg.delete()
            logger.info(f"Échec\n")

        await logs(interaction, f"execute la commande /presence")

        inscritsIds = []
        absentPresentIds = []
        rawVocalIds = []

        logger.info("+ Récupération des Ids !")

        api_key = settings.raid_helper_token
        url = f"https://raid-helper.dev/api/v2/events/{annonce_raid.id}"
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
        warning = True

        msg = f"**__Joueurs absents :__**\n"
        if len(absentsInscritsIds) > 0:
            for absentsInscritsId in absentsInscritsIds:
                msg += f"- {absentsInscritsId}\n"
        else:
            msg += "**Aucun**\n"
            warning = False

        if len(absentVocalIds) > 0:
            msg += f"\n**__Joueur non inscrits :__**\n"
            for absentVocalId in absentVocalIds:
                msg += f"- {absentVocalId}\n"

        if len(absentPresentIds) > 0:
            msg += f"\n**__Absents présents :__**\n"
            for absentPresentId in absentPresentIds:
                msg += f"- {absentPresentId}\n"

        msg_presence = await interaction.followup.send(
            embed=embed_success("", f"Le résultat se trouve dans {chan_commandes.jump_url} !")
        )

        msg_embed = f"Présence de {annonce_raid.jump_url} par {interaction.user.mention} :\n\n"
        msg_embed += msg[:-1]
        if warning:
            await chan_commandes.send(embed=embed_warning("", msg_embed))
        else:
            await chan_commandes.send(embed=embed_success("", msg_embed))

        logger.info("Succès\n")

        await asyncio.sleep(10)
        await msg_presence.delete()


def setup(bot):
    bot.add_cog(Presence(bot))
