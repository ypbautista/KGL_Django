from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:fragebogen_id>/<int:person_id>/abschnitt/<int:abschnitt_nr>/",
        views.abschnitt_ausfuellen,
        name="abschnitt_ausfuellen",
    ),

    path(
        "success/",
        views.success,
        name="success",
    ),
]