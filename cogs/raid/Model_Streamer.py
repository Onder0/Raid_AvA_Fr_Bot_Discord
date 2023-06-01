from peewee import *
from database.database import database


class Streamer(Model):
    id_membre = TextField(primary_key=True)
    nom_membre = TextField(default="")

    class Meta:
        database = database
