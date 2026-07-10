from django.contrib import admin

from .models import (
    JugendlichePerson,
    Bezugsperson,
    Fragebogen,
    FragebogenFall,
    Einladung,
    FragebogenAntwort,
    FragebogenAbschnitt,
    FrageVorlage,
    AbschnittFrage,
    AbschnittAntwort,
    FrageAntwort,
)



admin.site.register(
    JugendlichePerson
)


admin.site.register(
    Bezugsperson
)


admin.site.register(
    Fragebogen
)


admin.site.register(
    FragebogenFall
)



@admin.register(Einladung)
class EinladungAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "fall",
        "bezugsperson",
        "benutzt",
        "code",
    )



@admin.register(FragebogenAntwort)
class FragebogenAntwortAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "einladung",
        "start_time",
        "end_time",
    )



@admin.register(FragebogenAbschnitt)
class FragebogenAbschnittAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "fragebogen",
        "titel",
        "reihenfolge",
    )



@admin.register(FrageVorlage)
class FrageVorlageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "text",
    )



@admin.register(AbschnittFrage)
class AbschnittFrageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "fragebogen_abschnitt",
        "frage_vorlage",
        "reihenfolge",
    )



@admin.register(AbschnittAntwort)
class AbschnittAntwortAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "fragebogen_antwort",
        "fragebogen_abschnitt",
        "kommentar",
    )



@admin.register(FrageAntwort)
class FrageAntwortAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "abschnitt_antwort",
        "frage",
        "antwort_wert",
    )