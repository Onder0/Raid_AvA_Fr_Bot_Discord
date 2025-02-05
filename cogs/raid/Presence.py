from utils import *
from config import *
import nextcord
from nextcord import slash_command, message_command, Interaction
import requests
import datetime
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
        chan_raid_fs = interaction.guild.get_channel(settings.chan_annonces_raids_FS)
        chan_raid_bw = interaction.guild.get_channel(settings.chan_annonces_raids_BW)
        if interaction.channel != chan_raid_fs and interaction.channel != chan_raid_bw:
            error_msg = await interaction.followup.send(
                embed=embed_error(
                    "", f"Vous devez effectuer cette commande dans un chan d'annonce de raid !"
                )
            )
            logger.warning(
                f"- La commande a été exécutée dans {interaction.channel} au lieu d'un chan d'annonce raid !"
            )
            await asyncio.sleep(10)
            await error_msg.delete()
            logger.info(f"Échec\n")

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /presence !"
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)

        if not interaction.user.voice:
            error_msg = await interaction.followup.send(
                embed=embed_error(
                    "",
                    f"Vous devez être connecté a un channel vocal !",
                )
            )
            logger.warning(
                f"- {interaction.user.display_name} n'est pas connecté à un salon vocal !"
            )
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
        voc_chan = interaction.user.voice.channel

        for member in voc_chan.members:
            rawVocalIds.append(member.id)
        vocalIds = [f"<@{id}>" for id in rawVocalIds]
        logger.info("+ Ids des joueurs en voc récupérées !")

        absentsInscritsIds = set(inscritsIds) - set(vocalIds)
        absentVocalIds = set(vocalIds) - set(inscritsIds) - set(absentPresentIds)

        # ===== Gestion du message ===== #

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

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

        msg_embed = f"{interaction.user.mention} execute /presence à `{current_time}`\n{annonce_raid.jump_url} vs {voc_chan.mention}\n\n"
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
