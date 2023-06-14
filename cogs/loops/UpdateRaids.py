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
        try:
            await update_liste_raids(self)
        except Exception as e:
            logger.error(f"Échec: {e}\n")

    @liste_raids.before_loop
    async def before_boucle(self):
        await self.bot.wait_until_ready()


async def update_liste_raids(self):
    server_id = settings.guild_id[0]
    api_key = settings.raid_helper_token

    url = f"https://raid-helper.dev/api/v2/servers/{server_id}/events"
    headers = {"Authorization": api_key}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.warning(
            f"Échec de la requête à l'API Raid Helper => Status : {response.status_code}\n"
        )
        return
    data = response.json()

    await update_liste_ville(self, data, "fs")
    await update_liste_ville(self, data, "bw")


async def update_liste_ville(self, data, ville):
    bot_id = settings.bot_id
    chan_ville = f"chan_annonces_raids_{ville}"
    chan_raid = self.bot.get_channel(getattr(settings, chan_ville))

    events = [event for event in data["postedEvents"] if int(event["channelId"]) == chan_raid]
    events = sorted(events, key=lambda event: event["startTime"])

    events_by_day = {}

    server_id = settings.guild_id[0]
    guild = chan_raid.guild
    calendrier = nextcord.utils.get(guild.emojis, name="calendrier")
    groupe = nextcord.utils.get(guild.emojis, name="groupe")

    for event in events:
        start_time = event["startTime"]
        event_date = datetime.datetime.fromtimestamp(start_time).strftime("%d-%m-%Y")
        event_hour = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M")
        event_signup = event["signUpsAmount"]
        event_title = event["title"]

        event_url = f"https://discord.com/channels/{server_id}/{event['channelId']}/{event['id']}"

        if event_date not in events_by_day:
            events_by_day[event_date] = []

        events_by_day[event_date].append(
            f"> `{event_hour}`  {groupe}  `{event_signup}` **[{event_title}]({event_url})** <t:{start_time}:R>"
        )

    if ville == "fs":
        embed = nextcord.Embed(
            title="⚪ Liste des Raids - Fort Sterling ⚪", color=nextcord.Color.light_grey()
        )
    elif ville == "bw":
        embed = nextcord.Embed(
            title="🟠 Liste des Raids - Bridgewatch 🟠", color=nextcord.Color.orange()
        )

    for event_date, event_list in events_by_day.items():
        events_str = "\n".join(event_list)
        embed.add_field(name=f"{calendrier}  {event_date}", value=events_str, inline=False)

    if len(events) == 0:
        embed.add_field(name="Il n'y a pas de raids actuellement", value="\n", inline=False)

    if embed is None:
        logger.warning(f"Échec: Update liste raid - Erreur de création de l'embed !\n")
        return

    embed.add_field(
        name="",
        value=f"Les infos sont actualisées toutes les {settings.time_loop_update_raids} minutes.",
    )

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


def setup(bot):
    bot.add_cog(UpdateRaids(bot))
