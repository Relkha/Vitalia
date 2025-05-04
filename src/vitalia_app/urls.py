from django.urls import path
from vitalia_app.views import reservation_visite  # importer ta vue
from vitalia_app.views import surveillance_view

urlpatterns = [
    path('reservation-visite/', reservation_visite, name='reservation_visite'),
    path('surveillance/', surveillance_view, name='surveillance'),

]

