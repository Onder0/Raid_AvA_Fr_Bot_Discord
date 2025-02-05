from utils import *
from config import *
import nextcord
from nextcord import slash_command, Interaction, SlashOption
from nextcord.ext import commands


class Bonus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Bonus.py is ready!")

    @slash_command(name="bonus", description="Donne le rôle 🌟 Bonus 🌟 aux malheureux non pris.")
    async def bonus(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(
            description="Personne à laquelle donner le 🌟 Bonus 🌟 !", required=False
        ),
    ):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        if personne == None:
            logger.info(
                f"{interaction.user.id}: {interaction.user.display_name} execute la commande /bonus."
            )
        else:
            logger.info(
                f"{interaction.user.id}: {interaction.user.display_name} execute la commande /bonus {personne.display_name} ."
            )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        # Récupère le rôle MOR
        role = nextcord.utils.get(interaction.guild.roles, id=settings.bonus)
        # Récupère le channel texte bonus
        chan_bonus = interaction.guild.get_channel(settings.chan_bonus)
        # Récupère le channel vocal attente-bonus
        voc_attente_bonus = nextcord.utils.get(
            interaction.guild.voice_channels, id=settings.voc_attente_bonus
        )

        message = ""
        embed = ""

        if personne:
            await personne.add_roles(role)
            await chan_bonus.send(
                embed=embed_success(
                    "",
                    f"{interaction.user.mention} a donné le rôle {role.mention} à {personne.mention}",
                )
            )
            message += f"Le rôle bonus à bien été attribué à {personne.mention} !"
            logger.info(f"+ Bonus donné à {personne.display_name} .")
            embed = embed_success("", message)
            await ghostPing(chan_bonus, personne)
            await interaction.followup.send(
                embed=embed_success("", f"Le {role.mention} a bien été attribué.")
            )
        else:
            # Donne le rôle Bonus (MOR) aux personnes dans le channel vocal sélectionné et les ping dans le channel texte MOR
            # S'il y a des personnes dans le chan attente et dans le vocal ciblé, exécute, sinon envoie un message d'erreur
            if voc_attente_bonus.members:
                message += f"{interaction.user.mention} a donné le rôle Bonus à\n"
                for membre in voc_attente_bonus.members:
                    await membre.add_roles(role)
                    message += f"- {membre.mention}"
                    await ghostPing(chan_bonus, membre)
                embed = embed_success("", message)
                await chan_bonus.send(embed=embed)
                message += f"\nqui attendai(en)t dans {voc_attente_bonus.mention} !"
                embed = message
                logger.info(f"+ Les rôles ont été ajoutés dans le chan {voc_attente_bonus}")
            else:
                message += f"\n:warning: Personne ne se trouvais dans le chan {voc_attente_bonus.mention} ! :warning:"
                logger.warning(f"- Il n'y avait personne dans {voc_attente_bonus}")
                embed = embed_error("", message)
            await interaction.followup.send(
                embed=embed_success("", f"Les {role.mention} ont bien été attribués.")
            )

        logger.info(f"Succès !\n")
        if personne == None:
            await logs(interaction, f"execute la commande /bonus")
        else:
            await logs(interaction, f"execute la commande /bonus {personne.mention}")


def setup(bot):
    bot.add_cog(Bonus(bot))
