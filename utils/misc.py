from config import *
import nextcord


async def ghostPing(channel, personne):
    msg = await channel.send(personne.mention)
    await msg.delete()
    return
