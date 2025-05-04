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
from vitalia_app.views import index, propos, contact, connexion, message_admin, dashboard, connected_objects

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
    path("soins/", views.dossiers_medical, name="dossiers_medical"),
    path("soins/<int:pk>/", views.document_patient, name="document_patient"),
    path("soins/<int:pk>/modifier/", views.modifier_patient, name="modifier_patient"),
    path('soins/assigner/<int:pk>/', views.assigner_infirmier, name='assigner_infirmier'),
    path('dossier/<int:pk>/export_pdf/', views.export_dossier_pdf, name='export_dossier_pdf'),
    path('dossiers/export/pdf/', views.export_all_dossiers_pdf, name='export_all_dossiers_pdf'),



]
