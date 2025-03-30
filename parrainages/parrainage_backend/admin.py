from django.contrib import admin
from .models import Electeur, Candidat, Parrainage, Agent

@admin.register(Electeur)
class ElecteurAdmin(admin.ModelAdmin):
    list_display = ("id","nom", "prenom", "cin", "numero_electeur", "bureau_vote")
    search_fields = ("nom", "prenom", "cin", "numero_electeur")

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ("electeur", "email", "code", "parti_politique")
    search_fields = ("electeur__nom", "electeur__prenom", "email", "code")

@admin.register(Parrainage)
class ParrainageAdmin(admin.ModelAdmin):
    list_display = ("electeur", "candidat", "date_parrainage")
    search_fields = ("electeur__nom", "candidat__electeur__nom")

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "user", "role")
    search_fields = ("nom", "prenom", "role")
