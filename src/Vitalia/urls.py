"""Vitalia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from vitalia_app import views
from vitalia_app.views import index, propos, contact, connexion, message_admin, dashboard, connected_objects, event_list, planning_events_api, liste_chambres, connected_objects, surveillance_view, nos_services

urlpatterns = [
    path('admin/', admin.site.urls, name = 'admin'),
    path('',index, name='index'),
    path('a_propos/', propos, name ='a_propos'),
    path('contact/', contact, name = 'contact'),
    path('connexion/', connexion, name = 'connexion'),
    path('messages/', message_admin, name = 'message_admin'),
    path('repondre/<int:message_id>/', views.repondre_message, name='repondre_message'),
    path('dashboard/', dashboard, name = 'dashboard' ),
    path('logout/', views.deconnexion, name='deconnexion'),
    path('objets/', connected_objects, name='objets'),
    path('events/', event_list, name='event_list'),
    #path('events/create/', views.create_event, name='create_event'),
    #path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('mon_planning/', views.planning_individuel, name='planning_individuel'),
    path('planning_residents/', views.planning_residents, name='planning_residents'),
    path('mon_planning_resident/', views.planning_resident_individuel, name='mon_planning_resident'),
    path('chambres/', views.liste_chambres, name='liste_chambres'),
    path('chambres/<int:chambre_id>/modifier/', views.modifier_chambre, name='modifier_chambre'),
    path('api/planning_events/', planning_events_api, name='planning_events_api'),
    path('objets/', connected_objects, name='objets'),
    path('', include('vitalia_app.urls')),
    path('surveillance/', surveillance_view, name='surveillance'),
    path('services/', nos_services, name = 'services'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)