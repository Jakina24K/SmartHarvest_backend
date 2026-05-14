from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import user_connected_view, culture_caracteristics,culture_from_caracteristics, UsersViewSet, ZoneViewSet, SoilTypeViewSet, SeasonViewSet, zoneProfileViewSet, PlantViewSet, RecommendationLogViewSet,recommend_plants,predict, disease_solution, scan_and_solution, assistant_chat
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', user_connected_view, name='user_connected_view'),
    path('api/disease/predict/', predict, name='disease_predict'),
    path('api/disease/solution/', disease_solution, name='disease_solution'),
    path('api/assistant-chat/', assistant_chat, name='assistant_chat'),
    path('api/disease/', scan_and_solution, name='scan_solution'),
    path('api/culture_caracteristics/', culture_caracteristics, name='culture_caracteristics'),
    path('api/culture_from_caracteristics/', culture_from_caracteristics, name='culture_from_caracteristics'),
]
