from django.urls import path
from . import views

urlpatterns = [
    path(
        "start/<uuid:code>/",
        views.fragebogen_start,
        name="fragebogen_start",
    ),
    path(
        "start/<uuid:code>/abschnitt/<int:abschnitt_nr>/",
        views.abschnitt_ausfuellen,
        name="abschnitt_ausfuellen",
    ),

    path(
        "success/",
        views.success,
        name="success",
    ),
]