from utils import *
from config import *
import nextcord
from nextcord import slash_command, user_command, SlashOption, Interaction
from nextcord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Roles.py is ready!")

    @slash_command(name="offtank")
    async def off_tank(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "off_tank")

    @user_command(name="Off-tank")
    async def off_tank_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "off_tank")

    @slash_command(name="arcanes")
    async def arcanes(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "arcanes")

    @user_command(name="Arcanes")
    async def arcanes_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "arcanes")

    @slash_command(name="healer")
    async def healer(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "healer")

    @user_command(name="Healer")
    async def healer_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "healer")

    @slash_command(name="souchefer")
    async def souchefer(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "souchefer")

    @user_command(name="Souchefer")
    async def souchefer_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "souchefer")

    @slash_command(name="support")
    async def support(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "support")

    @user_command(name="Support")
    async def support_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "support")

    @slash_command(name="hpcut")
    async def hp_cut(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "hp_cut")

    @user_command(name="HP Cute")
    async def hp_cut_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "hp_cut")

    @slash_command(name="dps")
    async def dps(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "dps")

    @user_command(name="DPS")
    async def dps_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "dps")

    @slash_command(name="scout")
    async def scout(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "scout")

    @user_command(name="Scout")
    async def scout_user(self, interaction: Interaction, personne: nextcord.Member):
        await add_role(interaction, personne, "scout")


async def add_role(interaction: Interaction, personne: nextcord.Member, role_to_add: str):
    await interaction.response.defer()
    if not verif_guild(interaction):
        return

    logger.info(
        f"{interaction.user.id}: {interaction.user.display_name} execute la commande /{role_to_add} {personne.display_name}"
    )

    chan_commandes = interaction.guild.get_channel(settings.chan_commandes)
    cat_tickets = nextcord.utils.get(interaction.guild.categories, id=settings.cat_tickets)
    if interaction.channel != chan_commandes and interaction.channel.category.id != cat_tickets.id:
        error_msg = await interaction.followup.send(
            embed=embed_error(
                "",
                f"Vous devez effectuer cette commande dans le channel {chan_commandes.mention} ou dans un ticket de {cat_tickets.mention} !",
            )
        )
        logger.warning(
            f"- La commande a été exécutée dans {interaction.channel} au lieu de {chan_commandes} ou un chan de {cat_tickets} !"
        )
        await asyncio.sleep(10)
        await error_msg.delete()
        logger.info(f"Échec\n")
        return

    await logs(interaction, f"execute la commande /{role_to_add} {personne.mention}")

    role = nextcord.utils.get(interaction.guild.roles, id=getattr(settings, role_to_add))
    await personne.add_roles(role)
    logger.info(f"+ Role {role} ajouté à {personne.display_name}")

    await interaction.followup.send(
        embed=embed_success("", f"{personne.mention} est maintenant {role.mention} !")
    )
    if interaction.channel.category.id == cat_tickets.id:
        await ghostPing(interaction.channel, personne)
    logger.info("Succès\n")


def setup(bot):
    bot.add_cog(Roles(bot))
