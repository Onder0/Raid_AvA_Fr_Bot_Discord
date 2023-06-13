from config import *
import nextcord


async def ghostPing(channel, personne):
    msg = await channel.send(personne.mention)
    await msg.delete()
    return


async def logs(interaction, msg):
    from utils.embedder import embed_warning

    chan_logs = interaction.guild.get_channel(settings.chan_logs)
    await chan_logs.send(embed=embed_warning("", f"{interaction.user.mention} {msg}"))
