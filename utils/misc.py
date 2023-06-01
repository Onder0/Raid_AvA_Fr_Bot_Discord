import asyncio
import nextcord
from config import logger
from config import settings

async def ghostPing(channel, personne):
	msg = await channel.send(personne.mention)
	await msg.delete()
	return

async def verif_guild(interaction):
	# Envoie un message d'erreur si la guilde n'est pas whitelist 
	if interaction.guild.id not in settings.guild_id :
		from utils.embedder import embed_error
		error_msg = interaction.followup.send(embed=embed_error("","Votre serveur n'est pas autorisé à utiliser ce bot !"))
		logger.warning(f"Échec: Le serveur n'était pas autorisé=> id = {interaction.guild_id}.")
		logger.warning(f"=> nom : {interaction.guild.name} / id : {interaction.guild.id}\n")
		await asyncio.sleep(60)
		await error_msg.delete()
		return False
	return True

async def verif_chan(interaction, channel):
	# Si le message n'est pas dans commandes, afficher une erreur
	if (interaction.channel != channel) :
		from utils.embedder import embed_error
		error_msg = await interaction.followup.send(embed=embed_error("",
								f"Vous devez effectuer cette commande dans le channel {channel.mention} !"))
		logger.warning(f"Échec: La commande a été exécutée dans {interaction.channel} au lieu de {channel} !\n")
		await asyncio.sleep(10)
		await error_msg.delete()
		return False
	return True

async def verif_category(interaction, category_id):
	if (interaction.channel.category != category_id):
		from utils.embedder import embed_error
		error_msg = await interaction.followup.send(embed=embed_error("",
								f"Vous ne pouvez pas effectué la commande ici !"))
		logger.warning(f"Échec: La commande a été exécutée dans {interaction.channel} !\n")
		await asyncio.sleep(10)
		await error_msg.delete()
		return False
	return True
		