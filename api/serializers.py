from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email','password', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)

class UsersSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model= Users
        fields = '__all__'
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = self.fields['user']
            user_serializer.update(instance.user, user_data)

        return super().update(instance, validated_data)

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
