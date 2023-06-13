from peewee import *
from database.database import database


class Rankup(Model):
    id_membre = TextField(primary_key=True)
    nom_membre = TextField(default="")
    off_tank = SmallIntegerField(default=0)
    healer = SmallIntegerField(default=0)
    arcanes = SmallIntegerField(default=0)
    souchefer = SmallIntegerField(default=0)
    support = SmallIntegerField(default=0)
    hp_cut = SmallIntegerField(default=0)
    dps = SmallIntegerField(default=0)
    scout = SmallIntegerField(default=0)

    class Meta:
        database = database


from peewee import *
from database.database import database
