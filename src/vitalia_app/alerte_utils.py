from datetime import datetime
from .models import Alertes, ConnectedObject
from django.conf import settings


def create_alert(title, description, priority, alert_type, device=None, resident=None):
    """
    Fonction principale pour créer une alerte et envoyer des notifications
    depuis views.py
    """


def check_bracelet_alerts(bracelet):
    """Vérifie l'état d'un bracelet connecté et génère des alertes si nécessaire"""
    # Vérifier les données de santé
    heart_rate = bracelet.get_heart_rate()
    if heart_rate > 120:  # Fréquence cardiaque élevée
        create_alert(
            title=f"Fréquence cardiaque élevée - {bracelet.resident.user.first_name} {bracelet.resident.user.last_name}",
            description=f"La fréquence cardiaque du résident est de {heart_rate} bpm, ce qui est anormalement élevé.",
            priority="high",
            alert_type="medical",
            device=bracelet,
            resident=bracelet.resident
        )

    # Vérifier l'activité
    if bracelet.is_inactive_too_long():
        create_alert(
            title=f"Inactivité prolongée - {bracelet.resident.user.first_name} {bracelet.resident.user.last_name}",
            description="Le bracelet connecté n'a pas détecté de mouvement depuis une période prolongée.",
            priority="medium",
            alert_type="medical",
            device=bracelet,
            resident=bracelet.resident
        )


def check_air_quality_sensors():
    """Vérifie les capteurs de qualité de l'air et génère des alertes si nécessaire"""
    air_sensors = ConnectedObject.objects.filter(type="air_quality")

    for sensor in air_sensors:
        # Vérifier les niveaux de CO2
        co2_level = sensor.get_data("co2")
        if co2_level > 1500:  # ppm
            create_alert(
                title=f"Taux de CO2 élevé - {sensor.location}",
                description=f"Le niveau de CO2 est de {co2_level} ppm dans {sensor.location}, ce qui dépasse les seuils recommandés.",
                priority="medium",
                alert_type="environmental",
                device=sensor
            )

        # Vérifier les particules
        pm25_level = sensor.get_data("pm25")
        if pm25_level > 35:  # μg/m³
            create_alert(
                title=f"Qualité de l'air dégradée - {sensor.location}",
                description=f"Le niveau de particules fines (PM2.5) est de {pm25_level} μg/m³ dans {sensor.location}, ce qui est considéré comme malsain.",
                priority="medium",
                alert_type="environmental",
                device=sensor
            )


def check_door_sensors():
    """Vérifie les capteurs de porte et génère des alertes si nécessaire"""
    door_sensors = ConnectedObject.objects.filter(type="door_sensor")

    # Récupérer l'heure actuelle
    current_time = datetime.now().time()
    night_time = current_time.hour >= 22 or current_time.hour < 6

    for sensor in door_sensors:
        # Vérifier si la porte est ouverte trop longtemps
        if sensor.get_data("open") and sensor.get_data("duration_open") > 300:  # 5 minutes
            create_alert(
                title=f"Porte ouverte - {sensor.location}",
                description=f"La porte de {sensor.location} est restée ouverte pendant plus de 5 minutes.",
                priority="low",
                alert_type="security",
                device=sensor
            )

        # Vérifier les ouvertures de porte pendant la nuit
        if night_time and sensor.get_data("opened_recently"):
            create_alert(
                title=f"Ouverture de porte nocturne - {sensor.location}",
                description=f"La porte de {sensor.location} a été ouverte pendant la nuit.",
                priority="medium",
                alert_type="security",
                device=sensor
            )