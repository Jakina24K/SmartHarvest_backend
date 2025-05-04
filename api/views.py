from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,action
from datetime import date
from .models import Users, Zone, SoilType, Season, ZoneProfile, Plant, RecommendationLog
from .serializers import UsersSerializer, ZoneSerializer, SoilTypeSerializer, SeasonSerializer, ZoneProfileSerializer, PlantSerializer, RecommendationLogSerializer
from .permission import IsAdminUserProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import face_recognition
import numpy as np
import dlib 

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.select_related('user').all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminUserProfile]
    
    def perform_create(self, serializer):
        instance = serializer.save()

        if instance.photo:
            try:
                image_path = instance.photo.path

                rgb_image = dlib.load_rgb_image(image_path)
                
                face_detector = dlib.get_frontal_face_detector()
                
                print("Qu'est ce qui se passe dans face detector : ", face_detector)
                
                detections = face_detector(rgb_image, 1)
                
                print(f"Nombre de visages détectés par dlib : {len(detections)}")
                
                print("Ici on commence a utilisé face recognition")
                
                face_locations = face_recognition.face_locations(rgb_image)
                if not face_locations:
                    print("Aucun visage détecté dans l'image.")
                    return

                encodings = face_recognition.face_encodings(rgb_image, face_locations)

                if encodings:
                    instance.face_encoding = encodings[0].tolist()
                    instance.save()
                else:
                    print("Encodage impossible même après détection.")
            except Exception as e:
                print(f"Erreur de traitement de l'image : {e}")
    @action(detail=False, methods=['get','patch'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            profile = Users.objects.select_related('user').get(user=request.user)
        except Users.DoesNotExist:
            return Response({"detail": "Profil non trouvé."}, status=404)
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)


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

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data

    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return Response({'error': f'{field} is required'}, status=400)

    try:
        # Check if username or email already exists
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=400)
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=400)

        # Create the User instance
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password'])  # Hash the password
        )

        # Create the Users profile
        Users.objects.create(
            user=user,
            localisation=data.get('localisation', ''),
            photo=data.get('photo', None),
            role=data.get('role', 'user')
        )

        return Response({'message': 'User created successfully'}, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['GET'])
def recommend_plants(request):
    zone_id = request.query_params.get('zone_id')
    if not zone_id:
        return Response({'error': 'zone_id is required'}, status=400)

    try:
        zone_profile = ZoneProfile.objects.select_related(
            'soil_type', 'zone').get(zone__id=zone_id)
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
