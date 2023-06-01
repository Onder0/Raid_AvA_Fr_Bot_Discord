from peewee import *
from database.database import database


class NoShow(Model):
    id_membre = TextField(primary_key=True)
    nom_membre = TextField(default="")
    no_show_count = SmallIntegerField(default=0)
    no_show_total = SmallIntegerField(default=0)
    dernier_pardon = DateTimeField(null=True)
    id_auteur_pardon = TextField(null=True)
    nom_auteur_pardon = TextField(null=True)

    class Meta:
        database = database

