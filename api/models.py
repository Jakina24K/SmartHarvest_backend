from django.db import models
from django.contrib.auth.models import User

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    localisation = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(upload_to='faces/', null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class Zone(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class SoilType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Season(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    start_month = models.DateField(null=False)
    end_month = models.DateField(null=False)

    def __str__(self):
        return self.name


class Plant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)
    soil_type = models.ManyToManyField(SoilType)
    season = models.ManyToManyField(Season)

    def __str__(self):
        return self.name


class ZoneProfile(models.Model):
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE)
    soil_type = models.ForeignKey(
        SoilType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.zone.name} - {self.soil_type.name}"


class RecommendationLog(models.Model):
    zone = models.ForeignKey('ZoneProfile', on_delete=models.CASCADE)
    plant = models.ForeignKey('Plant', on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone.zone_name} - {self.plant.name} - {self.season.name}"
