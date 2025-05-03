from django.urls import path
from vitalia_app.views import reservation_visite  # importer ta vue

urlpatterns = [
    path('reservation-visite/', reservation_visite, name='reservation_visite'),
]

