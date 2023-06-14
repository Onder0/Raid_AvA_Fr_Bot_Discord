from utils import *
from config import *
import nextcord
from nextcord import SlashOption, slash_command, Interaction
from nextcord.ext import commands
from cogs.management.Model_Rankup import Rankup


ROLES = [
    {"name": "Off-Tank", "value": "off_tank"},
    {"name": "Healer", "value": "healer"},
    {"name": "Arcanes", "value": "arcanes"},
    {"name": "Souchefer", "value": "souchefer"},
    {"name": "Support", "value": "support"},
    {"name": "HP Cut", "value": "hp_cut"},
    {"name": "DPS", "value": "dps"},
    {"name": "Scout", "value": "scout"},
]


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        Rankup.create_table()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Rank.py is ready!")

    @slash_command(
        name="rankup",
        description="Ajoute un +1 dans le rôle sélectionné à la personne sélectionnée.",
    )
    async def rankup(
        self,
        interaction: Interaction,
        role: str = SlashOption(
            description="Le rôle pour lequel elle va être rankup.",
            required=True,
            choices=[choice["name"] for choice in ROLES],
        ),
        personne: nextcord.Member = SlashOption(description="La personne à rankup.", required=True),
    ):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /rankup {role} {personne.display_name} ."
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        role_rankup = None
        for choice in ROLES:
            if choice["name"] == role:
                role_rankup = choice["value"]
                break
        role_normal = nextcord.utils.get(interaction.guild.roles, id=getattr(settings, role_rankup))
        if role != "HP Cut":
            role_rankup_expert = f"{role_rankup}_expert"
            role_expert = nextcord.utils.get(
                interaction.guild.roles, id=getattr(settings, role_rankup_expert)
            )
        elite_expert = nextcord.utils.get(interaction.guild.roles, id=settings.elite_expert)
        if role == "Support":
            hp_cut = nextcord.utils.get(interaction.guild.roles, id=settings.hp_cut)
        if role == "HP Cut":
            support_expert = nextcord.utils.get(interaction.guild.roles, id=settings.support_expert)

        result_rankup, created = Rankup.get_or_create(id_membre=personne.id)
        setattr(result_rankup, "nom_membre", personne.display_name)
        result_rankup.save()

        plus_un = getattr(result_rankup, role_rankup)

        message = ""
        embed = ""
        message_commande = ""
        embed_commande = ""

        expert = False
        elite = False

        if role != "Scout" and elite_expert in personne.roles:
            message += f":crown: :fire: {personne.mention} est déjà {elite_expert.mention} ! :fire: :crown:\n"
            message_commande += f"{personne.mention} est déjà {elite_expert.mention} !"
            expert = True
            logger.info(f"+ {personne.display_name} est déjà {elite_expert}")

        elif role == "HP Cut":
            if plus_un == 1:
                if getattr(result_rankup, "support") == 5:
                    message += (
                        f":star2: {personne.mention} est déjà {support_expert.mention} ! :start2:"
                    )
                    message_commande += f"{personne.mention} est déjà {support_expert.mention}"
                    logger.info(f"+ {personne.display_name} est déjà {support_expert}")
                else:
                    message += f"{personne.mention} est déjà {role_normal} !"
                    message_commande += f"{personne.mention} est déjà {role_normal}"
                    logger.info(f"+ {personne.display_name} est déjà {role_normal}")
                embed = embed_warning("", message)
                embed_commande = embed_success("", message)
            else:
                plus_un += 1
                setattr(result_rankup, role_rankup, plus_un)
                result_rankup.save()
                if getattr(result_rankup, "support") == 5:
                    support = nextcord.utils.get(interaction.guild.roles, id=settings.support)
                    support_expert = nextcord.utils.get(
                        interaction.guild.roles, id=settings.support_expert
                    )
                    await personne.remove_roles(role_normal)
                    await personne.remove_roles(support)
                    await personne.add_roles(support_expert)
                    expert = True
                    elite = await verif_elite(interaction, personne)
                    message += f":star2: {personne.mention} est maintenant {support_expert.mention} ! :star2:"
                    message_commande += (
                        f"{personne.mention} est maintenant {support_expert.mention}"
                    )
                    logger.info(f"+ {personne.display_name} est maintenant {support_expert}")
                else:
                    await personne.add_roles(role_normal)
                    message += f":star2: {personne.mention} est maintenant {role_normal.mention} ! :star2:\n"
                    message_commande += f"{personne.mention} est maintenant {role_normal.mention}"
                    logger.info(f"+ {personne.display_name} est maintenant {role_normal}")
        else:
            if plus_un == 5:
                if role == "Support" and getattr(result_rankup, "hp_cut") == 0:
                    message += f"{personne.mention} est déjà +5 {role_normal.mention} mais n'est pas {hp_cut.mention} !"
                    message_commande += f"{personne.mention} +5 {role_normal} mais pas {hp_cut}"
                    logger.info(
                        f"{personne.display_name} est déjà +5 {role_normal.mention} mais n'est pas {hp_cut} !"
                    )
                else:
                    message += (
                        f":star2: {personne.mention} est déjà {role_expert.mention} ! :star2:\n"
                    )
                    message_commande += f"{personne.mention} est déjà {role_expert.mention}"
                    expert = True
                    logger.info(f"+ {personne.display_name} est déjà {role_expert}")
            else:
                plus_un += 1
                setattr(result_rankup, role_rankup, plus_un)
                result_rankup.save()
                if plus_un == 5:
                    if role == "Support" and getattr(result_rankup, "hp_cut") == 0:
                        message += f"{personne.mention} a atteint +5 {role_normal.mention} mais pas {hp_cut.mention} !"
                        message_commande += (
                            f"{personne.mention} +5 {role_normal.mention} mais pas {hp_cut} !"
                        )
                        logger.info(
                            f"{personne.display_name} est déjà +5 {role_normal.mention} mais pas {hp_cut} !"
                        )
                    else:
                        if role == "Support":
                            await personne.remove_roles(hp_cut)
                        await personne.remove_roles(role_normal)
                        await personne.add_roles(role_expert)
                        expert = True
                        elite = await verif_elite(interaction, personne)
                        message += f":star2: {personne.mention} a atteint le +5, il est maintenant {role_expert.mention} ! :star2:"
                        message_commande += f"{personne.mention} a atteint {role_expert.mention}"
                        logger.info(f"+ {personne.display_name} est maintenant {role_expert}")

                else:
                    await personne.add_roles(role_normal)
                    message += (
                        f"{personne.mention} est maintenant {role_normal.mention} +{plus_un} !"
                    )
                    message_commande += f"{personne.mention} {role_normal.mention} +{plus_un}"
                    logger.info(f"+ {personne.display_name} est {role_normal} +{plus_un} .")

        if elite:
            await personne.add_roles(elite_expert)
            message = f":crown: :fire: **{personne.mention} passe {elite_expert.mention} !** :fire: :crown:"
            message_commande = f"{personne.mention} {elite_expert.mention} !"
            logger.info(f"+ {personne.display_name} est maintenant {elite_expert}")

        if expert:
            embed = embed_warning("", message)
        else:
            embed = embed_success("", message)

        embed_commande = embed_success("", message_commande)

        await interaction.followup.send(embed=embed_commande)
        chan_rankup = interaction.guild.get_channel(settings.chan_rankup)
        await chan_rankup.send(embed=embed)

        await ghostPing(chan_rankup, personne)
        logger.info(f"Succès !\n")
        await logs(interaction, f"execute la commande /rankup {role} {personne.mention}")

    # ========== ========== ========== ========== ========== ========== ========== ========== ========== #

    @slash_command(
        name="derank",
        description="Enlève un +1 dans le rôle sélectionné à la personne sélectionnée.",
    )
    async def derank(
        self,
        interaction: Interaction,
        personne: nextcord.Member = SlashOption(description="La personne à dérank", required=True),
        role: str = SlashOption(
            description="Le rôle pour lequel elle va être rankup.",
            required=True,
            choices=[choice["name"] for choice in ROLES],
        ),
        raison: str = SlashOption(description="La raison de son dérank.", required=True),
    ):
        await interaction.response.defer()
        if not await verif_guild(interaction):
            return

        logger.info(
            f"{interaction.user.id}: {interaction.user.display_name} execute la commande /derank {role} {personne.display_name} {raison}."
        )

        chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
        if not await verif_chan(interaction, chan_commandes):
            return

        role_rankup = None
        for choice in ROLES:
            if choice["name"] == role:
                role_rankup = choice["value"]
                break
        role_normal = nextcord.utils.get(interaction.guild.roles, id=getattr(settings, role_rankup))

        result_rankup, created = Rankup.get_or_create(id_membre=personne.id)
        setattr(result_rankup, "nom_membre", personne.display_name)

        plus_un = getattr(result_rankup, role_rankup)
        if plus_un == 0:
            logger.warning(f"- {personne.display_name} n'avait pas de +1 en {role_normal} !")
            interaction.followup.send(
                embed=embed_error(
                    "", f"{personne.mention} n'avait pas de +1 en {role_normal.mention} !"
                )
            )
            return
        else:
            plus_un -= 1

        setattr(result_rankup, role_rankup, plus_un)
        result_rankup.save()

        message = ""

        if plus_un == 4:
            role_rankup_expert = f"{role_rankup}_expert"
            role_expert = nextcord.utils.get(
                interaction.guild.roles, id=getattr(settings, role_rankup_expert)
            )
            await personne.remove_roles(role_expert)
            await personne.add_roles(role_normal)
            message += f"{personne.mention} n'est plus {role_expert.mention} !\nIl est revenu à {role_normal.mention} +{plus_un} !"
            logger.info(
                f"+ {personne.display_name} n'est plus {role_expert}. => {role_normal} +{plus_un}."
            )
        elif plus_un == 0:
            message += f"{personne.mention} n'est plus rank en {role_normal.mention} !"
            logger.info(f"+ {personne.display_name} n'est plus rank en {role_normal}.")
        else:
            message += f"{personne.mention} est revenu à {role_normal.mention} +{plus_un} !"
            logger.info(f"+ {personne.display_name} est {role_normal} +{plus_un}.")
        message += f"\n`=> {raison}`"

        chan_rankup = interaction.guild.get_channel(settings.chan_rankup)
        await chan_rankup.send(embed=embed_error("", message))
        await interaction.followup.send(embed=embed_warning("", message))
        await ghostPing(chan_rankup, personne)
        logger.info(f"Succès !\n")
        await logs(interaction, f"execute la commande /derank {role} {personne.mention} {raison}")


async def verif_elite(interaction, personne):
    rankup = Rankup.get(Rankup.id_membre == personne.id)
    fields = rankup._meta.fields
    for field_name, field in fields.items():
        if field_name not in ["id_membre", "nom_membre", "hp_cut", "scout"]:
            value = getattr(rankup, field_name)
            if value != 5:
                return False
    if rankup.hp_cut == 0:
        return False

    for role in ROLES:
        if role["value"] not in ["hp_cut", "scout"]:
            role_expert_name = f"{role['value']}_expert"
            role_expert = nextcord.utils.get(
                interaction.guild.roles, id=getattr(settings, role_expert_name)
            )
            await personne.remove_roles(role_expert)
    hp_cut = nextcord.utils.get(interaction.guild.roles, id=settings.hp_cut)
    await personne.remove_roles(hp_cut)

    return True


def setup(bot):
    bot.add_cog(Rank(bot))
