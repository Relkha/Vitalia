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
from django.urls import path
from vitalia_app import views
from vitalia_app.views import index, propos, contact, connexion, message_admin, dashboard, connected_objects, event_list

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
    path('events/', event_list, name='event-list'),
    ]
