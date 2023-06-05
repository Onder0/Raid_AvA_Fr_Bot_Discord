from config import *
import asyncio


async def verif_guild(interaction):
    # Envoie un message d'erreur si la guilde n'est pas whitelist
    if interaction.guild.id not in settings.guild_id:
        from utils.embedder import embed_error

        error_msg = await interaction.followup.send(
            embed=embed_error("", "Votre serveur n'est pas autorisé à utiliser ce bot !")
        )
        logger.warning(f"Échec: Le serveur n'était pas autorisé=> id = {interaction.guild_id}.")
        logger.warning(f"=> nom : {interaction.guild.name} / id : {interaction.guild.id}\n")
        await asyncio.sleep(60)
        await error_msg.delete()
        return False
    return True


async def verif_chan(interaction, channel):
    chan_temp = interaction.guild.get_channel(settings.chan_temp)
    if interaction.channel != channel and interaction.channel != chan_temp:
        from utils.embedder import embed_error

        error_msg = await interaction.followup.send(
            embed=embed_error(
                "", f"Vous devez effectuer cette commande dans le channel {channel.mention} !"
            )
        )
        logger.warning(
            f"- La commande a été exécutée dans {interaction.channel} au lieu de {channel} !"
        )
        await asyncio.sleep(10)
        await error_msg.delete()
        logger.info(f"Échec\n")
        return False
    return True


async def verif_thread(interaction, thread):
    chan_temp = interaction.guild.get_channel(settings.chan_temp)
    if interaction.channel != thread and interaction.channel != chan_temp:
        from utils.embedder import embed_error

        error_msg = await interaction.followup.send(
            embed=embed_error(
                "", f"Vous devez effectuer cette commande dans le thread {thread.mention} !"
            )
        )
        logger.warning(
            f"- La commande a été exécutée dans {interaction.channel} au lieu de {thread} !"
        )
        await asyncio.sleep(10)
        await error_msg.delete()
        logger.info(f"Échec\n")
        return False
    return True


async def verif_categorie(interaction, categorie):
    chan_temp = interaction.guild.get_channel(settings.chan_temp)
    if interaction.channel.category_id != categorie.id and interaction.channel != chan_temp:
        from utils.embedder import embed_error

        error_msg = await interaction.followup.send(
            embed=embed_error(
                "",
                f"Vous devez effectuer cette commande dans un channel de la catégorie {categorie.mention} !",
            )
        )
        logger.warning(
            f"- La commande a été exécutée dans {interaction.channel} au lieu d'un channel de la catégorie {categorie} !"
        )
        await asyncio.sleep(10)
        await error_msg.delete()
        logger.info(f"Échec\n")
        return False
    return True
