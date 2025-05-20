from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, permission_classes, action
from datetime import date
from .models import Users, Zone, SoilType, Season, ZoneProfile, Plant, RecommendationLog
from .serializers import UsersSerializer, ZoneSerializer, SoilTypeSerializer, SeasonSerializer, ZoneProfileSerializer, PlantSerializer, RecommendationLogSerializer
from .permission import IsAdminUserProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import numpy as np
from deepface import DeepFace
from rest_framework_simplejwt.tokens import RefreshToken
import tempfile
import os
from api.scripts.plant_process import preprocess_image, model, class_names, nom_classe
from decouple import config
from api.scripts.solution_desease import generate_content
import torch
import logging

logger = logging.getLogger(__name__)

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.select_related('user').all()
    serializer_class = UsersSerializer
    permission_classes = [IsAdminUserProfile]

    @action(detail=False, methods=['get', 'patch'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            profile = Users.objects.select_related(
                'user').get(user=request.user)
        except Users.DoesNotExist:
            return Response({"detail": "Profil non trouvé."}, status=404)
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                profile, data=request.data, partial=True)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_connected_view(request):
    profile = Users.objects.get(user=request.user)
    return Response({
        "username": request.user.username,
        "email": request.user.email,
        "role": profile.role
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def facial_auth_view(request):
    image_file = request.FILES.get('photo')

    if not image_file:
        return Response({"detail": "Aucune image fournie."}, status=400)

        # Sauvegarde temporaire du fichier image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        for chunk in image_file.chunks():
            tmp_file.write(chunk)
            tmp_path = tmp_file.name

    try:
        users = Users.objects.exclude(face_encoding__isnull=True)
        for user in users:
            if not user.face_encoding:
                continue
            result = DeepFace.verify(
                img1_path=tmp_path,
                img2_path=user.photo.path,
                model_name='Facenet',
                enforce_detection=False
            )
            print("Résultat de l'analyse : ",result)
            if result["distance"] <= 0.7:
                result["verified"] = True
                
            if result["verified"]:
                    # Authentification réussie
                refresh = RefreshToken.for_user(user.user)
                os.remove(tmp_path)
                return Response({
                    "refresh": str(refresh),
                     "access": str(refresh.access_token),
                     "username": user.user.username
                })

        os.remove(tmp_path)
        return Response({"detail": "Visage non reconnu."}, status=401)

    except Exception as e:
            os.remove(tmp_path)
            return Response({"detail": f"Erreur : {str(e)}"}, status=500)
        

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    print("Les données recus sont : ", data)
    files = request.FILES
    

    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return Response({'error': f'{field} is required'}, status=400)

    try:
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Username already exists'}, status=400)
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=400)

        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password'])
        )

        photo = files.get('photo')

        user_profile = Users.objects.create(
            user=user,
            localisation=data.get('localisation', ''),
            photo=photo,
            role=data.get('role', 'user')
        )

        # Process the photo with DeepFace if it exists
        if user_profile.photo:
            try:
                image_path = user_profile.photo.path

                representations = DeepFace.represent(
                    img_path=image_path,
                    model_name='Facenet',  # or 'VGG-Face', 'ArcFace', etc.
                    enforce_detection=True
                )

                if representations and len(representations) > 0:
                    embedding = representations[0]["embedding"]
                    user_profile.face_encoding = embedding
                    user_profile.save()
                    print("Encodage facial enregistré avec succès.")
                else:
                    print("Aucune représentation faciale extraite.")
            except Exception as e:
                print(f"Erreur avec DeepFace : {e}")

        return Response({'message': 'User created successfully'}, status=201)

    except Exception as e:
        print(f"Error : {str(e)}")
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

@api_view(['POST'])
@permission_classes([AllowAny])
def predict(request):
    print("Le fichier recu : ",request.FILES)
    try:
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=400)
        
        img_bytes = request.FILES['file'].read()
        input_tensor = preprocess_image(img_bytes)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            pred_name = class_names[pred_class]
            pred_prob = probs[0][pred_class].item()

        response = {
            "class_name": pred_name,
            "probability": round(pred_prob, 4)
        }
        logger.info(f"Prediction response: {response}")
        return Response(response)
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        return Response({"error": f"Error in predict: {e}"}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def disease_solution(request):
    MODEL = config('MODEL')
    VERSION = config('VERSION')
    GOOGLE_API_KEY = config('GOOGLE_API_KEY')

    # Extract data from POST request
    data = request.data
    cleaned_theme = data.get('cleaned_theme')
    text = data.get('text')
    mode = data.get('mode', 'Agonnome')

    # Validate required fields
    if not all([MODEL, VERSION, GOOGLE_API_KEY, "Ravinkazo", text]):
        return Response(
            {'error': 'Missing required fields or environment variables'},
            status=HTTP_400_BAD_REQUEST
        )

    try:
        # Call the original function
        response = generate_content(
            MODEL, VERSION, GOOGLE_API_KEY, cleaned_theme, text, mode=mode
        )
        return Response({'result': response}, status=HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def scan_and_solution(request):
    try:
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=400)
        
        MODEL = config('MODEL')
        VERSION = config('VERSION')
        GOOGLE_API_KEY = config('GOOGLE_API_KEY')

        data = request.data
        mode = data.get('mode', 'agricultural engineer')

        # Validate required fields
        if not all([MODEL, VERSION, GOOGLE_API_KEY, "Ravinkazo"]):
            return Response(
                {'error': 'Missing required fields or environment variables'},
                status=HTTP_400_BAD_REQUEST
            )
        
        img_bytes = request.FILES['file'].read()
        input_tensor = preprocess_image(img_bytes)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            pred_name = class_names[pred_class]
            pred_name_desc = nom_classe[pred_class]
            pred_prob = probs[0][pred_class].item()

        predict = {
            "class_name": pred_name_desc,
            "probability": f"{round(pred_prob*100, 4)}%"
        }
        logger.info(f"Prediction response: {predict}")
        response = generate_content(
            MODEL, VERSION, GOOGLE_API_KEY, "Ravinkazo", predict, mode=mode
        )
        return Response({
            'prediction': predict,
            'resultat': response
            }, status=HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        return Response({"error": f"Error in predict: {e}"}, status=500)
