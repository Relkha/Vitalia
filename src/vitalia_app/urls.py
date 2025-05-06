from django.urls import path
from vitalia_app.views import reservation_visite  # importer ta vue
from vitalia_app.views import surveillance_view
from . import views

urlpatterns = [
    path('reservation-visite/', reservation_visite, name='reservation_visite'),
    path('surveillance/', surveillance_view, name='surveillance'),
    path('objets-connectes/', views.connected_objet_view, name='objets_connectes'),
    path('objets-connectes/modifier/<int:pk>/', views.update_connected_object, name='update_connected_object'),
    path('objets-interactifs/', views.objets_interactifs_view, name='objets_interactifs'),


]

