from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ZoneViewSet, SoilTypeViewSet, SeasonViewSet, zoneProfileViewSet, PlantViewSet, RecommendationLogViewSet, recommend_plants

router = DefaultRouter()
router.register(r'zones', ZoneViewSet)
router.register(r'soil_types', SoilTypeViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'zone_profiles', zoneProfileViewSet)
router.register(r'plants', PlantViewSet)
router.register(r'recommendation_logs', RecommendationLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/recommend_plants/', recommend_plants, name='recommend_plants'),  # Add standalone path
]
