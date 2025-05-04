from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import user_connected_view, register_view, UsersViewSet, ZoneViewSet, SoilTypeViewSet, SeasonViewSet, zoneProfileViewSet, PlantViewSet, RecommendationLogViewSet, recommend_plants
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'zones', ZoneViewSet)
router.register(r'users', UsersViewSet)
router.register(r'soil_types', SoilTypeViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'zone_profiles', zoneProfileViewSet)
router.register(r'plants', PlantViewSet)
router.register(r'recommendation_logs', RecommendationLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/recommend_plants/', recommend_plants, name='recommend_plants'),  # Add standalone path
    path('api/register/', register_view, name='register_view'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', user_connected_view, name='user_connected_view'),
]
