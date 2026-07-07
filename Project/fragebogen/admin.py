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
)

admin.site.register(JugendlichePerson)
admin.site.register(Bezugsperson)
admin.site.register(Fragebogen)
admin.site.register(FragebogenAntwort)
admin.site.register(FrageAntwort)
admin.site.register(AbschnittAntwort)
admin.site.register(AbschnittFrage)
admin.site.register(FrageVorlage)
admin.site.register(FragebogenAbschnitt)