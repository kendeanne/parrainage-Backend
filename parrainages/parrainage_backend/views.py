from rest_framework import viewsets, status, generics, permissions
from .models import Electeur, Candidat, Parrainage, Agent, Configuration, PeriodeParrainage, HistoriqueImportation
from .serializers import (
    ElecteurSerializer, 
    CandidatSerializer, 
    ParrainageSerializer, 
    AgentSerializer,
    PeriodeParrainageSerializer,
    CreateParrainageSerializer
)
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import random
import string
from django.db.models import Count, Q
from datetime import datetime
from django.utils.timezone import make_aware
import csv
from io import StringIO
from django.db.models.functions import TruncDate
from functools import wraps

# ==================== DÉCORATEUR CORS ====================
def add_cors_headers(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        response = view_func(*args, **kwargs)
        if isinstance(response, Response):
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"  # 24h cache for CORS preflight
        return response
    return wrapper

# ==================== VIEWSETS ====================
class CorsModelViewSet(viewsets.ModelViewSet):
    @add_cors_headers
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ElecteurViewSet(CorsModelViewSet):
    queryset = Electeur.objects.all()
    serializer_class = ElecteurSerializer

class CandidatViewSet(CorsModelViewSet):
    queryset = Candidat.objects.select_related('electeur').all()
    serializer_class = CandidatSerializer

    @add_cors_headers
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ParrainageViewSet(CorsModelViewSet):
    queryset = Parrainage.objects.all()
    serializer_class = ParrainageSerializer

class AgentViewSet(CorsModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

# ==================== API VIEWS ====================
@api_view(['POST'])
@add_cors_headers
def login_candidat(request):
    email = request.data.get('email')
    code = request.data.get('code')

    try:
        candidat = Candidat.objects.get(email=email, code=code)
        electeur = candidat.electeur
        return Response({
            'success': True,
            'candidat_id': candidat.id,
            'nom': electeur.nom,
            'prenom': electeur.prenom,
            'email': candidat.email,
            'telephone': candidat.telephone,
            'slogan': candidat.slogan,
            'date_enregistrement': candidat.date_enregistrement,
            'site_web': candidat.site_web,
            'parti_politique': candidat.parti_politique,
            'code': candidat.code,
        })
    except Candidat.DoesNotExist:
        return Response({'success': False, 'error': 'Email ou code invalide'}, status=400)

@api_view(['POST'])
@add_cors_headers
def generate_code_for_candidat(request):
    email = request.data.get('email')
    try:
        candidat = Candidat.objects.get(email=email)
        candidat.code = candidat.generer_code()
        candidat.save()
        return Response({
            'success': True,
            'message': f"Le code du candidat {candidat.electeur.nom} {candidat.electeur.prenom} a été généré.",
            'code': candidat.code,
        })
    except Candidat.DoesNotExist:
        return Response({'error': 'Candidat non trouvé'}, status=404)

@api_view(['GET'])
@add_cors_headers
def get_parrainages_candidat(request, candidat_id):
    try:
        candidat = Candidat.objects.get(id=candidat_id)
        parrainages = Parrainage.objects.filter(candidat=candidat)
        serializer = ParrainageSerializer(parrainages, many=True)
        return Response(serializer.data)
    except Candidat.DoesNotExist:
        return Response({'error': 'Candidat non trouvé'}, status=404)

@api_view(['POST'])
@add_cors_headers
def import_electeurs(request):
    if Electeur.objects.exists():
        HistoriqueImportation.objects.create(
            user_name=request.data.get('userName'),
            user_prenom=request.data.get('userPrenom'),
            user_ip=request.data.get('userIp'),
            message="Importation échouée : La table Electeur contient déjà des données."
        )
        return Response(
            {'message': 'La table Electeur contient déjà des données. Importation interdite.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_ip = request.data.get('userIp')
    user_name = request.data.get('userName')
    user_prenom = request.data.get('userPrenom')
    
    if 'file' not in request.FILES:
        return Response({'message': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

    csv_file = request.FILES['file']
    
    try:
        csv_data = csv_file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(csv_data))
        electeurs_a_inserer = []
        
        for row in reader:
            if not all(k in row for k in ['cin', 'numero_electeur', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'bureau_vote', 'sexe']):
                HistoriqueImportation.objects.create(
                    user_name=user_name,
                    user_prenom=user_prenom,
                    user_ip=user_ip,
                    message="Importation échouée : Format du fichier incorrect."
                )
                return Response({'message': 'Le fichier CSV ne contient pas les colonnes attendues.'}, status=status.HTTP_400_BAD_REQUEST)

            electeurs_a_inserer.append(Electeur(
                cin=row['cin'],
                numero_electeur=row['numero_electeur'],
                nom=row['nom'],
                prenom=row['prenom'],
                date_naissance=row['date_naissance'],
                lieu_naissance=row['lieu_naissance'],
                bureau_vote=row['bureau_vote'],
                sexe=row['sexe']
            ))

        Electeur.objects.bulk_create(electeurs_a_inserer)
        return Response({'message': 'Importation réussie !'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        HistoriqueImportation.objects.create(
            user_name=user_name,
            user_prenom=user_prenom,
            user_ip=user_ip,
            message=f"Importation échouée : {str(e)}"
        )
        return Response({'message': 'Erreur lors de limportation du fichier.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@add_cors_headers
def update_periode_parrainage(request):
    try:
        periode = PeriodeParrainage.objects.latest('debut')
    except PeriodeParrainage.DoesNotExist:
        return Response({"detail": "Aucune période de parrainage trouvée."}, status=status.HTTP_404_NOT_FOUND)

    now = make_aware(datetime.now())
    if periode.debut > now:
        return Response(
            {"detail": "Vous ne pouvez pas redéfinir les dates tant que la période de parrainage actuelle n'est pas expirée."},
            status=status.HTTP_400_BAD_REQUEST
        )

    new_debut = request.data.get('debut')
    new_fin = request.data.get('fin')
    periode.debut = new_debut
    periode.fin = new_fin
    periode.save()

    return Response({"detail": "Période de parrainage mise à jour avec succès."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@add_cors_headers
def verifier_electeur(request, numero_electeur):
    try:
        electeur = Electeur.objects.get(numero_electeur=numero_electeur)
        return Response({
            'exists': True,
            'electeur_id': electeur.id,
            'nom': electeur.nom,
            'prenom': electeur.prenom,
            'numero_electeur': electeur.numero_electeur,
            'bureau_vote': electeur.bureau_vote,
            'cin': electeur.cin,
            'lieu_naissance': electeur.lieu_naissance
        })
    except Electeur.DoesNotExist:
        return Response({'exists': False}, status=404)

@api_view(['POST'])
@add_cors_headers
def ajouter_candidat(request):
    numero_electeur = request.data.get('electeur')
    try:
        electeur = Electeur.objects.get(numero_electeur=numero_electeur)
    except Electeur.DoesNotExist:
        return Response({'error': 'Électeur non trouvé'}, status=status.HTTP_400_BAD_REQUEST)

    data = {
        'electeur': electeur.id,
        'email': request.data.get('email'),
        'telephone': request.data.get('telephone'),
        'parti_politique': request.data.get('parti_politique'),
        'slogan': request.data.get('slogan'),
        'site_web': request.data.get('site_web'),
    }

    serializer = CandidatSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@add_cors_headers
def monitoring_parrainages(request):
    date_filter = request.query_params.get('date', None)
    queryset = Parrainage.objects.all()
    
    if date_filter:
        target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        queryset = queryset.filter(date_parrainage__date=target_date)
    
    results = (
        queryset
        .values('candidat__id', 'candidat__electeur__nom', 'candidat__electeur__prenom')
        .annotate(
            total=Count('id'),
            valides=Count('id', filter=Q(electeur__isnull=False))
        )
        .order_by('-total')
    )
    return Response(list(results))

@api_view(['GET'])
@add_cors_headers
def get_total_parrainages_requis(request):
    try:
        config = Configuration.objects.latest('id')
        return Response({'total_parrainages_requis': config.parrainages_requis})
    except Configuration.DoesNotExist:
        return Response({'total_parrainages_requis': 1000})

@api_view(['GET'])
@add_cors_headers
def get_evolution_parrainages(request, candidat_id):
    parrainages = (
        Parrainage.objects
        .filter(candidat=candidat_id)
        .annotate(date=TruncDate('date_parrainage'))
        .values('date')
        .annotate(total=Count('id'))
        .order_by('date')
    )
    return Response(parrainages)

# ==================== CLASS BASED VIEWS ====================
class CandidatListView(APIView):
    @add_cors_headers
    def get(self, request):
        try:
            candidats = Candidat.objects.select_related('electeur').all()
            serializer = CandidatSerializer(candidats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ParrainageCreateAPIView(generics.CreateAPIView):
    queryset = Parrainage.objects.all()
    serializer_class = ParrainageSerializer

    @add_cors_headers
    def create(self, request, *args, **kwargs):
        try:
            electeur_id = request.data.get('electeur')
            candidat_id = request.data.get('candidat')
            
            if not electeur_id or not candidat_id:
                return Response(
                    {"error": "Les champs electeur et candidat sont requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Electeur.objects.get(id=electeur_id)
            Candidat.objects.get(id=candidat_id)
            
            if Parrainage.objects.filter(electeur_id=electeur_id).exists():
                return Response(
                    {"error": "Cet électeur a déjà parrainé un candidat"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            parrainage = Parrainage.objects.create(
                electeur_id=electeur_id,
                candidat_id=candidat_id
            )
            
            return Response(
                {
                    "success": True,
                    "parrainage_id": parrainage.id,
                    "message": "Parrainage enregistré avec succès"
                },
                status=status.HTTP_201_CREATED
            )
            
        except Electeur.DoesNotExist:
            return Response({"error": "Électeur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        except Candidat.DoesNotExist:
            return Response({"error": "Candidat non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PeriodeAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @add_cors_headers
    def post(self, request):
        serializer = PeriodeParrainageSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('est_active'):
                PeriodeParrainage.objects.filter(est_active=True).update(est_active=False)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckPeriodAPI(APIView):
    permission_classes = []

    @add_cors_headers
    def get(self, request):
        periode = PeriodeParrainage.objects.filter(est_active=True).first()
        if periode:
            return Response({
                'is_active': periode.est_en_cours(),
                'date_debut': periode.date_debut,
                'date_fin': periode.date_fin
            })
        return Response({
            'is_active': False,
            'detail': 'Aucune période configurée'
        }, status=status.HTTP_404_NOT_FOUND)

# ==================== OPTIONS HANDLER ====================
@api_view(['OPTIONS'])
@add_cors_headers
def cors_options(request):
    return Response(status=200)