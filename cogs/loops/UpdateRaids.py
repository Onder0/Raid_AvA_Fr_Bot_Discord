from utils import *
from config import *
import nextcord
from nextcord.ext import commands, tasks
import requests


class UpdateRaids(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liste_raids.start()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("UpdateRaids.py is ready!")

    @tasks.loop(minutes=settings.time_loop_update_raids)
    async def liste_raids(self):
        # print(f"Update liste raid en cours !\n")
        try:
            await verif_liste_raid(self)
        except Exception as e:
            logger.error(f"Échec: {e}\n")

    @liste_raids.before_loop
    async def before_boucle(self):
        await self.bot.wait_until_ready()


async def verif_liste_raid(self):
    bot_id = settings.bot_id
    chan_raid_bw = self.bot.get_channel(settings.chan_annonces_raids_bw)
    chan_raid_fs = self.bot.get_channel(settings.chan_annonces_raids_fs)
    server_id = settings.guild_id[0]
    api_key = settings.raid_helper_token

    url = f"https://raid-helper.dev/api/v2/servers/{server_id}/events"
    headers = {"Authorization": api_key}

    response = requests.get(url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        data = response.json()

        events_bw = [
            event for event in data["postedEvents"] if int(event["channelId"]) == chan_raid_bw.id
        ]
        events_fs = [
            event for event in data["postedEvents"] if int(event["channelId"]) == chan_raid_fs.id
        ]

        events_bw = sorted(events_bw, key=lambda event: event["startTime"])
        events_fs = sorted(events_bw, key=lambda event: event["startTime"])

        events_by_day_bw = {}
        events_by_day_fs = {}

        guild = chan_raid_bw.guild
        calendrier = nextcord.utils.get(guild.emojis, name="calendrier")
        groupe = nextcord.utils.get(guild.emojis, name="groupe")

        for event in events_bw:
            start_time = event["startTime"]
            event_date = datetime.datetime.fromtimestamp(start_time).strftime("%d-%m-%Y")
            event_hour = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M")
            event_signup = event["signUpsAmount"]
            event_title = event["title"]

            event_url = (
                f"https://discord.com/channels/{server_id}/{event['channelId']}/{event['id']}"
            )

            if event_date not in events_by_day_bw:
                events_by_day_bw[event_date] = []

            events_by_day_bw[event_date].append(
                f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>"
            )
        for event in events_fs:
            start_time = event["startTime"]
            event_date = datetime.datetime.fromtimestamp(start_time).strftime("%d-%m-%Y")
            event_hour = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M")
            event_signup = event["signUpsAmount"]
            event_title = event["title"]

            event_url = (
                f"https://discord.com/channels/{server_id}/{event['channelId']}/{event['id']}"
            )

            if event_date not in events_by_day_fs:
                events_by_day_fs[event_date] = []

            events_by_day_fs[event_date].append(
                f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>"
            )

        embed_bw = nextcord.Embed(title="Liste des Raids :", color=nextcord.Color.orange())
        embed_fs = nextcord.Embed(title="Liste des Raids :", color=nextcord.Color.light_grey())

        # Parcourir le dictionnaire des événements par jour et ajouter un champ à l'embed pour chaque jour avec la liste des événements pour ce jour
        for event_date, event_list in events_by_day_bw.items():
            # Joindre les événements pour ce jour en les séparant par des sauts de ligne
            events_str = "\n".join(event_list)
            # Ajouter le champ à l'embed avec la date de début comme nom et la liste des événements pour ce jour comme valeur
            embed_bw.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)
        for event_date, event_list in events_by_day_fs.items():
            events_str = "\n".join(event_list)
            embed_fs.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)

        if len(events_bw) == 0:
            embed_bw.add_field(name="Il n'y a pas de raids actuellement", value="\n", inline=False)
        if len(events_fs) == 0:
            embed_fs.add_field(name="Il n'y a pas de raids actuellement", value="\n", inline=False)

        # Ajouter le dernier champ avec des informations supplémentaires
        embed_bw.add_field(
            name="",
            value=f"Les infos sont actualisées toutes les {settings.time_loop_update_raids} minutes.",
        )
        embed_fs.add_field(
            name="",
            value=f"Les infos sont actualisées toutes les {settings.time_loop_update_raids} minutes.",
        )
    else:
        logger.warning(
            f"Échec de la requête à l'API Raid Helper => Status : {response.status_code}\n"
        )

    if embed_bw is None and embed_fs == None:
        return

    bot_message_id_bw = None
    bot_message_id_fs = None

    messages_bw = [message async for message in chan_raid_bw.history()]
    messages_fs = [message async for message in chan_raid_bw.history()]

    for index, message in enumerate(messages_bw):
        if message.author.id == bot_id:
            bot_message_id_bw = message.id
            break
    for index, message in enumerate(messages_fs):
        if message.author.id == bot_id:
            bot_message_id_fs = message.id
            break

    if bot_message_id_bw == None:
        await chan_raid_bw.send(embed=embed_bw)
    elif index != 0:
        await messages_bw[index].delete()
        await chan_raid_bw.send(embed=embed_bw)
    else:
        await message.edit(embed=embed_bw)

    if bot_message_id_fs == None:
        await chan_raid_fs.send(embed=embed_fs)
    elif index != 0:
        await messages_fs[index].delete()
        await chan_raid_fs.send(embed=embed_fs)
    else:
        await message.edit(embed=embed_fs)


def setup(bot):
    bot.add_cog(UpdateRaids(bot))
