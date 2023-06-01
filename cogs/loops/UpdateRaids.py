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
    chan_raid = self.bot.get_channel(settings.chan_annonces_raids)

    embed = await embed_liste_raid(self)

    if embed is None:
        return

    bot_message_id = None
    messages = [message async for message in chan_raid.history()]

    for index, message in enumerate(messages):
        if message.author.id == bot_id:
            bot_message_id = message.id
            break

    if bot_message_id == None:
        await chan_raid.send(embed=embed)
    elif index != 0:
        await messages[index].delete()
        await chan_raid.send(embed=embed)
    else:
        await message.edit(embed=embed)


async def embed_liste_raid(self):
    server_id = settings.guild_id[0]
    api_key = settings.raid_helper_token

    url = f"https://raid-helper.dev/api/v2/servers/{server_id}/events"
    headers = {"Authorization": api_key}

    # Envoyer une requête GET à l'API
    response = requests.get(url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Charger la réponse JSON
        data = response.json()

        chan_raid = self.bot.get_channel(settings.chan_annonces_raids)
        # Filtrer les événements pour ne conserver que ceux dans le channel #annonce-raid
        events = [
            event for event in data["postedEvents"] if int(event["channelId"]) == chan_raid.id
        ]

        # Tri des événements par date
        events = sorted(events, key=lambda event: event["startTime"])

        # Création d'un dictionnaire pour stocker les événements par jour
        events_by_day = {}

        guild = chan_raid.guild
        calendrier = nextcord.utils.get(guild.emojis, name="calendrier")
        groupe = nextcord.utils.get(guild.emojis, name="groupe")

        # Parcourir la liste des événements filtrés
        for event in events:
            start_time = event["startTime"]
            event_date = datetime.datetime.fromtimestamp(start_time).strftime("%d-%m-%Y")
            event_hour = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M")
            event_signup = event["signUpsAmount"]
            event_title = event["title"]

            event_url = (
                f"https://nextcord.com/channels/{server_id}/{event['channelId']}/{event['id']}"
            )

            # Si la date de début de l'événement n'est pas déjà présente dans le dictionnaire, l'ajouter avec une liste vide comme valeur
            if event_date not in events_by_day:
                events_by_day[event_date] = []

            # Ajouter l'événement à la liste des événements pour la date de début correspondante
            events_by_day[event_date].append(
                f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>"
            )

        # Création de l'embed Nextcord
        embed = nextcord.Embed(title="Liste des Raids :", color=nextcord.Color.teal())

        # Parcourir le dictionnaire des événements par jour et ajouter un champ à l'embed pour chaque jour avec la liste des événements pour ce jour
        for event_date, event_list in events_by_day.items():
            # Joindre les événements pour ce jour en les séparant par des sauts de ligne
            events_str = "\n".join(event_list)
            # Ajouter le champ à l'embed avec la date de début comme nom et la liste des événements pour ce jour comme valeur
            embed.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)

        if len(events) == 0:
            embed.add_field(name="Il n'y a pas de raids actuellement", value="\n", inline=False)

        # Ajouter le dernier champ avec des informations supplémentaires
        embed.add_field(
            name="",
            value=f"Les infos sont actualisées toutes les {settings.time_loop_update_raids} minutes.",
        )

        return embed
    else:
        logger.warning(
            f"Échec de la requête à l'API Raid Helper => Status : {response.status_code}\n"
        )


def setup(bot):
    bot.add_cog(UpdateRaids(bot))
