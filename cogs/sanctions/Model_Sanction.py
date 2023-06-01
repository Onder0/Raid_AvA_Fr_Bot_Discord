import datetime
import pytz
from peewee import *
from database.database import database

class Sanctions(Model):
    date = DateTimeField(default=datetime.datetime.now(tz=pytz.timezone('Europe/Paris')))
    id_membre = TextField(default="")
    nom_membre = TextField(default="")
    raison = TextField(default="")
    montant = TextField(default="")
    id_auteur = TextField(default="")
    nom_auteur = TextField(default="")

    class Meta:
        database = database
