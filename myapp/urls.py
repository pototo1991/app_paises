from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("principal/", views.principal, name="principal"),
    path("country/<str:country_name>/", views.country_detail, name="country_detail"),
    path("game/", views.game, name="game"),
    path("reset_counters/", views.reset_counters, name="reset_counters"),
    # otras rutas
]
