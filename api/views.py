from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import date
from .models import Zone, SoilType, Season, ZoneProfile, Plant, RecommendationLog
from .serializers import ZoneSerializer, SoilTypeSerializer, SeasonSerializer, ZoneProfileSerializer, PlantSerializer, RecommendationLogSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer


class SoilTypeViewSet(viewsets.ModelViewSet):
    queryset = SoilType.objects.all()
    serializer_class = SoilTypeSerializer


class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class zoneProfileViewSet(viewsets.ModelViewSet):
    queryset = ZoneProfile.objects.all()
    serializer_class = ZoneProfileSerializer


class PlantViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class RecommendationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RecommendationLog.objects.all().order_by('-recommended_at')
    serializer_class = RecommendationLogSerializer

@api_view(['GET'])
def recommend_plants(request):
    zone_id = request.query_params.get('zone_id')
    if not zone_id:
        return Response({'error': 'zone_id is required'}, status=400)

    try:
        zone_profile = ZoneProfile.objects.select_related('soil_type', 'zone').get(zone__id=zone_id)
    except ZoneProfile.DoesNotExist:
        return Response({'error': 'ZoneProfile not found'}, status=404)

    today = date.today()

    current_seasons = Season.objects.filter(
        start_month__month__lte=today.month,
        end_month__month__gte=today.month
    )

    if not current_seasons.exists():
        return Response({'error': 'No active season found'}, status=404)

    recommended_plants = Plant.objects.filter(
        soil_type=zone_profile.soil_type,
        season__in=current_seasons
    ).distinct()

    print('Recommended plants:', recommended_plants)
    print('current_seasons:', current_seasons)
    
    for plant in recommended_plants:
        RecommendationLog.objects.create(
            zone=zone_profile,
            plant=plant,
            season=current_seasons.first()
        )

    serializer = PlantSerializer(recommended_plants, many=True)
    return Response(serializer.data)