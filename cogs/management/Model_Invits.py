from peewee import *
from database.database import database
import datetime
import pytz


class Invits(Model):
    id_membre = TextField(default="")
    id_voucher = TextField(default="")
    date = DateField(default=datetime.datetime.now(tz=pytz.timezone("Europe/Paris")))

    class Meta:
        database = database
