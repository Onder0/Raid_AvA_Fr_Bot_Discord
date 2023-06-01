from peewee import *
from database.database import database

class Rankup(Model):
    id_membre = TextField(primary_key=True)
    nom_membre = TextField(default="")
    off_tank = SmallIntegerField(default=0)
    healer = SmallIntegerField(default=0)
    grand_arcane = SmallIntegerField(default=0)
    arcane = SmallIntegerField(default=0)
    souchefer = SmallIntegerField(default=0)
    mande_tenebre = SmallIntegerField(default=0)
    epee_tranchante = SmallIntegerField(default=0)
    brise_royaume = SmallIntegerField(default=0)
    chasse_esprit = SmallIntegerField(default=0)
    spectre = SmallIntegerField(default=0)
    frost = SmallIntegerField(default=0)
    fire = SmallIntegerField(default=0)
    arbalete = SmallIntegerField(default=0)
    scout = SmallIntegerField(default=0)
    
    class Meta:
        database = database
