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
from django.contrib.auth import views as auth_views

from vitalia_app import views
from vitalia_app.views import index, propos, contact, connexion, message_admin, dashboard, connected_objects, event_list, planning_events_api, liste_chambres, connected_objects, surveillance_view, alertes_dashboard, alert_details, acknowledge_alert, resolve_alert, notifications, unread_notifications, mon_profil, CustomPasswordChangeView, demande_compte, envoi_lien_reinit_password, formulaire_nouveau_mdp, upgrade_niveau, nos_services


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
    path('mon_planning/', views.planning_individuel, name='planning_individuel'),
    path('planning_residents/', views.planning_residents, name='planning_residents'),
    path('mon_planning_resident/', views.planning_resident_individuel, name='mon_planning_resident'),
    path('chambres/', views.liste_chambres, name='liste_chambres'),
    path('chambres/<int:chambre_id>/modifier/', views.modifier_chambre, name='modifier_chambre'),
    path('api/planning_events/', planning_events_api, name='planning_events_api'),
    path('', include('vitalia_app.urls')),
    path('surveillance/', surveillance_view, name='surveillance'),
    path("soins/", views.dossiers_medical, name="dossiers_medical"),
    path("soins/<int:pk>/", views.document_patient, name="document_patient"),
    path("soins/<int:pk>/modifier/", views.modifier_patient, name="modifier_patient"),
    path('soins/assigner/<int:pk>/', views.assigner_infirmier, name='assigner_infirmier'),
    path('dossier/<int:pk>/export_pdf/', views.export_dossier_pdf, name='export_dossier_pdf'),
    path('dossiers/export/pdf/', views.export_all_dossiers_pdf, name='export_all_dossiers_pdf'),
    path('alertes/', views.alertes_dashboard, name='alertes_dashboard'),
    path('api/alertes/<int:alert_id>/details/', views.alert_details, name='alert_details'),
    path('api/alertes/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('api/alertes/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('generate-test-alert/', views.generate_test_alert, name='generate_test_alert'),
    path("profil/", mon_profil, name="mon_profil"),
    path('profil/password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path("mot-de-passe-oublie/", envoi_lien_reinit_password, name="reinit_password_custom"),
    path("reinitialiser/<uidb64>/<token>/", formulaire_nouveau_mdp, name="reinit_password_confirm"),
    path('demande-compte/', demande_compte, name='demande_compte'),
    path("profil/upgrade-niveau/", upgrade_niveau, name="upgrade_niveau"),
    path("services/", nos_services, name = "services")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


