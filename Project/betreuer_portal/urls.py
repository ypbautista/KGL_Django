from django.urls import path
from . import views

app_name = "betreuer_portal"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("jugendliche/", views.jugendliche_list, name="jugendliche_list"),
    path("jugendliche/<int:jp_id>/", views.jugendliche_detail, name="jugendliche_detail"),
    path("generate-link/", views.generate_link, name="generate_link"),
]