from django.contrib import admin
from .models import (
    AbschnittAntwort,
    AbschnittFrage,
    FrageAntwort,
    FrageVorlage,
    FragebogenAbschnitt,
    FragebogenAntwort,
    JugendlichePerson,
    Bezugsperson,
    Fragebogen,
    Einladung,
)

admin.site.register(JugendlichePerson)
admin.site.register(Bezugsperson)
admin.site.register(Fragebogen)
@admin.register(FragebogenAntwort)
class FragebogenAntwortAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "jugendliche_person",
        "fragebogen",
        "bewertet_von",
        "start_time",
        "end_time",
    )
@admin.register(FrageAntwort)
class FrageAntwortAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "abschnitt_antwort",
        "frage",
        "antwort_wert",
    )
@admin.register(AbschnittAntwort)
class AbschnittAntwortAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fragebogen_antwort",
        "fragebogen_abschnitt",
        "kommentar",
    )
@admin.register(AbschnittFrage)
class AbschnittFrageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fragebogen_abschnitt",
        "frage_vorlage",
        "reihenfolge",
    )
@admin.register(FrageVorlage)
class FrageVorlageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
    )
@admin.register(FragebogenAbschnitt)
class FragebogenAbschnittAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fragebogen",
        "titel",
        "reihenfolge",
    )
@admin.register(Einladung)
class EinladungAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "jugendliche_person",
        "fragebogen",
        "erstellt_am",
        "benutzt",
    )