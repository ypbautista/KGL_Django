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
        "export/<int:fall_id>/",
        views.export_fragebogen_pdf,
        name="export_pdf",
    ),

    path(
        "success/",
        views.success,
        name="success",
    ),

]