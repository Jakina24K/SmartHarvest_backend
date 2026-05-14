from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, permission_classes, action
from datetime import date
from .models import Users, Zone, SoilType, Season, ZoneProfile, Plant, RecommendationLog
from .serializers import UsersSerializer, ZoneSerializer, SoilTypeSerializer, SeasonSerializer, ZoneProfileSerializer, PlantSerializer, RecommendationLogSerializer
from .permission import IsAdminUserProfile
from .services import get_culture_caracteristics, get_culture_from_caracteristics
from api.scripts.plant_process import preprocess_image, model, class_names, nom_classe, class_names_malagasy
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
def assistant_chat(request):
    MODEL = config('MODEL')
    VERSION = config('VERSION')
    GOOGLE_API_KEY = config('GOOGLE_API_KEY')

    data = request.data

    message = data.get('message')
    mode = data.get('mode', 'Agonnome')

    if not all([MODEL, VERSION, GOOGLE_API_KEY, message]):
        return Response(
            {'error': 'Missing required fields or environment variables'},
            status=HTTP_400_BAD_REQUEST
        )

    try:
        prompt = f"""
        You are an agricultural AI assistant for Madagasikara.

        Answer in Malagasy language when possible.

        User Message:
        {message}
        """

        response = generate_content(
            MODEL,
            VERSION,
            GOOGLE_API_KEY,
            "Hasimboly dia azensa misehatra amin'ny fambolena sy fiompina",
            prompt,
            mode="Agricultural Consultant"
        )

        return Response(
            {'result': response},
            status=HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def scan_and_solution(request):
    try:
        # 1. Vérification du fichier dans la requête
        uploaded_file = request.FILES.get('file', None)
        if not uploaded_file:
            return Response({"error": "Aucun fichier fourni"}, status=HTTP_400_BAD_REQUEST)

        # 2. Vérification des variables d'environnement
        MODEL = config('MODEL', default=None)
        VERSION = config('VERSION', default=None)
        GOOGLE_API_KEY = config('GOOGLE_API_KEY', default=None)
        DEFAULT_CONTEXT = "Ravinkazo"

        if not all([MODEL, VERSION, GOOGLE_API_KEY, DEFAULT_CONTEXT]):
            return Response(
                {'error': 'Variables d’environnement manquantes ou invalides'},
                status=HTTP_400_BAD_REQUEST
            )

        # 3. Lecture du mode (agriculteur, ingénieur, etc.)
        data = request.data
        mode = data.get('mode', 'agricultural engineer')

        # 4. Lecture et traitement de l’image
        try:
            img_bytes = uploaded_file.read()
            input_tensor = preprocess_image(img_bytes)  # Fonction que vous avez déjà
        except Exception as img_err:
            logger.error(f"Erreur de traitement de l’image : {img_err}")
            return Response({"error": "Image invalide ou non traitable"}, status=HTTP_400_BAD_REQUEST)

        # 5. Prédiction avec le modèle
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            pred_name = class_names[pred_class]
            pred_name_desc = nom_classe[pred_class]
            pred_class_names_malagasy = class_names_malagasy[pred_class]
            pred_prob = probs[0][pred_class].item()

        prediction = {
            "class_name_en": pred_name_desc,
            "class_name": pred_class_names_malagasy,
            "probability": f"{round(pred_prob * 100, 2)}%"
        }

        logger.info(f"Résultat de la prédiction : {prediction}")

        # 6. Génération de la réponse via un agent ou IA externe
        response_content = generate_content(
            MODEL, VERSION, GOOGLE_API_KEY, DEFAULT_CONTEXT, prediction, mode=mode
        )

        response_mg2 = generate_content(
            MODEL, VERSION, GOOGLE_API_KEY, DEFAULT_CONTEXT, prediction, mode="mpamboly ingeniera"
        )

        response_mg = generate_content(
            MODEL, VERSION, GOOGLE_API_KEY, DEFAULT_CONTEXT, prediction, mode="mpamboly ingeniera malagasy"
        )

        return Response({
            'prediction': prediction,
            'result_en': response_content,
            'result': response_mg,
            'result_mg': response_mg2
        }, status=HTTP_200_OK)

    except Exception as e:
        logger.exception("Erreur inattendue dans scan_and_solution")
        return Response({"error": f"Erreur interne du serveur : {e}"}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def culture_caracteristics(request):
    query = request.data.get('culture')
    query = query.lower()
    if not query:
        return Response({"error": "Veuillez fournir une culture à analyser"}, status=400)
        
    results = get_culture_caracteristics(query)

    if results:
        return Response({"caracteristics": results}, status=200)
    
    return Response({"error": "Erreur lors de la récuperation des caractétistiques de la culture"}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def culture_from_caracteristics(request):
    data = request.data.get('caracteristic')

    print("query", data)

    if not data:
        return Response(
            {"error": "Veuillez fournir les caractéristiques"},
            status=400
        )

    season = data.get("season", "").lower()

    results = get_culture_from_caracteristics(season)

    if results:
        return Response({"cultures": results}, status=200)

    return Response(
        {"error": "Erreur lors de la récupération des cultures"},
        status=500
    )
