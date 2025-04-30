from rest_framework import serializers
from .models import *


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class SoilTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilType
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class ZoneProfileSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    soil_type_name = serializers.CharField(
        source='soil_type.name', read_only=True)

    class Meta:
        model = ZoneProfile
        fields = ['id', 'zone', 'zone_name', 'soil_type', 'soil_type_name']


class PlantSerializer(serializers.ModelSerializer):
    soil_type = serializers.PrimaryKeyRelatedField(
        queryset=SoilType.objects.all(), many=True)
    season = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(), many=True)

    class Meta:
        model = Plant
        fields = '__all__'

class RecommendationLogSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.zone_name', read_only=True)
    soil_type_name = serializers.CharField(source='zone.soil_type.name', read_only=True)
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    zone_name = serializers.CharField(source='zone.zone.name', read_only=True)

    class Meta:
        model = RecommendationLog
        fields = [
            'id',
            'zone_name',
            'soil_type_name',
            'plant_name',
            'season_name',
            'zone_name',
            'recommended_at'
        ]
