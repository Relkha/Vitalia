from rest_framework import serializers
from .models import PlanningEventInfirmier, Evenement

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningEventInfirmier
        fields = ['subject', 'start_time', 'end_time']
