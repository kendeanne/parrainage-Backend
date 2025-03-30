from rest_framework import viewsets
from .models import Electeur, Candidat, Parrainage, Agent, Configuration
from .serializers import ElecteurSerializer, CandidatSerializer, ParrainageSerializer, AgentSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
import random
import string
from rest_framework import status
from django.db.models import Count
from .models import Electeur, HistoriqueImportation
import csv
from io import StringIO
from datetime import datetime
from rest_framework import status
from .models import PeriodeParrainage
from django.utils.timezone import make_aware
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Candidat
from .serializers import CandidatSerializer
from rest_framework import status
from django.db.models import Count
from datetime import datetime
from django.db.models import Q  # <-- Ajoutez cette ligne
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.views import View
from .models import Candidat
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Parrainage
from .serializers import CreateParrainageSerializer, ParrainageSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Parrainage
from .serializers import ParrainageSerializer, CreateParrainageSerializer


from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PeriodeParrainage
from .serializers import PeriodeParrainageSerializer
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import PeriodeParrainage
from .serializers import PeriodeParrainageSerializer







# ✅ Vue pour gérer les électeurs
class ElecteurViewSet(viewsets.ModelViewSet):
    queryset = Electeur.objects.all()
    serializer_class = ElecteurSerializer



#✅ Vue pour gérer les candidats
class CandidatViewSet(viewsets.ModelViewSet):
    queryset = Candidat.objects.select_related('electeur').all()
    serializer_class = CandidatSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ✅ Vue pour gérer les parrainages
class ParrainageViewSet(viewsets.ModelViewSet):
    queryset = Parrainage.objects.all()
    serializer_class = ParrainageSerializer

# ✅ Vue pour gérer les agents DGE
class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

@api_view(['POST'])
def login_candidat(request):
    # Récupérer l'email et le code envoyés dans la requête
    email = request.data.get('email')
    code = request.data.get('code')

    try:
        # Trouver le candidat avec l'email et le code de sécurité
        candidat = Candidat.objects.get(email=email, code=code)

        # Accéder aux informations de l'électeur lié au candidat
        electeur = candidat.electeur  # C'est ici que nous accédons à l'électeur

        # Renvoyer les informations du candidat et de l'électeur dans la réponse
        return Response({
            'success': True,
            'candidat_id': candidat.id,
            'nom': electeur.nom,  # Nom de l'électeur
            'prenom': electeur.prenom,  # Prénom de l'électeur
            'email': candidat.email,
            'telephone': candidat.telephone,
            'slogan': candidat.slogan,
            'date_enregistrement': candidat.date_enregistrement,
            'site_web': candidat.site_web,
            'parti_politique': candidat.parti_politique,
            'code': candidat.code,
        })

    except Candidat.DoesNotExist:
        # Si le candidat n'est pas trouvé
        return Response({'success': False, 'error': 'Email ou code invalide'}, status=400)

# ✅ Fonction pour générer un code pour un candidat
@api_view(['POST'])
def generate_code_for_candidat(request):
    email = request.data.get('email')
    try:
        candidat = Candidat.objects.get(email=email)
        
        # Générer un nouveau code
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
def get_parrainages_candidat(request, candidat_id):
    try:
        candidat = Candidat.objects.get(id=candidat_id)  # On récupère le candidat avec l'ID donné
        parrainages = Parrainage.objects.filter(candidat=candidat)  # On récupère ses parrainages
        serializer = ParrainageSerializer(parrainages, many=True)
        return Response(serializer.data)
    except Candidat.DoesNotExist:
        return Response({'error': 'Candidat non trouvé'}, status=404)
    


@api_view(['POST'])
def import_electeurs(request):
    """ Gère l'importation d'un fichier CSV contenant la liste des électeurs. """

    # Vérifier si la table Electeur est vide
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

    # Récupération des informations utilisateur
    user_ip = request.data.get('userIp')
    user_name = request.data.get('userName')
    user_prenom = request.data.get('userPrenom')
    checksum = request.data.get('checksum')

    # Vérification et lecture du fichier CSV
    if 'file' not in request.FILES:
        return Response({'message': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

    csv_file = request.FILES['file']
    
    try:
        csv_data = csv_file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(csv_data))

        electeurs_a_inserer = []
        for row in reader:
            # Vérification de la structure des données
            if not all(k in row for k in ['cin', 'numero_electeur', 'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'bureau_vote', 'sexe']):
                HistoriqueImportation.objects.create(
                    user_name=user_name,
                    user_prenom=user_prenom,
                    user_ip=user_ip,
                    message="Importation échouée : Format du fichier incorrect."
                )
                return Response({'message': 'Le fichier CSV ne contient pas les colonnes attendues.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validation des champs
            errors = []
            if len(row['cin']) > 15 or not row['cin'].isdigit():
                errors.append(f"CIN invalide: {row['cin']}")
            if len(row['numero_electeur']) > 15 or not row['numero_electeur'].isdigit():
                errors.append(f"Numéro électeur invalide: {row['numero_electeur']}")
            if not row['nom'].isalpha() or len(row['nom']) > 15:
                errors.append(f"Nom invalide: {row['nom']}")
            #if not row['prenom'].isalpha() or len(row['prenom']) > 30:
                #errors.append(f"Prénom invalide: {row['prenom']}")
            try:
                date_naissance = datetime.strptime(row['date_naissance'], '%Y-%m-%d')
                if (datetime.now() - date_naissance).days / 365 < 18:
                    errors.append(f"L'électeur doit avoir au moins 18 ans: {row['date_naissance']}")
            except ValueError:
                errors.append(f"Date de naissance invalide: {row['date_naissance']}")
            if not row['lieu_naissance'].isalnum() or len(row['lieu_naissance']) > 40:
                errors.append(f"Lieu de naissance invalide: {row['lieu_naissance']}")
              
            #if not row['bureau_vote'].isalnum() or len(row['bureau_vote']) > 191:
            #    errors.append(f"Bureau de vote invalide: {row['bureau_vote']}")
            if row['sexe'] not in ['M', 'F']:
                errors.append(f"Sexe invalide: {row['sexe']}")

            if errors:
                # Si des erreurs sont trouvées, on les logge et retourne l'erreur
                HistoriqueImportation.objects.create(
                    user_name=user_name,
                    user_prenom=user_prenom,
                    user_ip=user_ip,
                    message=f"Importation échouée : {', '.join(errors)}"
                )
                return Response({'message': f"Erreurs de validation : {', '.join(errors)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Si aucune erreur, préparer l'insertion des électeurs
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

        # Enregistrement en base de données
        Electeur.objects.bulk_create(electeurs_a_inserer)

        return Response({'message': 'Importation réussie !'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        HistoriqueImportation.objects.create(
            user_name=user_name,
            user_prenom=user_prenom,
            user_ip=user_ip,
            message=f"Importation échouée : {str(e)}"
        )
        return Response({'message': 'Erreur lors de l’importation du fichier.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_periode_parrainage(request):
    # Vérifier s'il existe une période active
    try:
        periode = PeriodeParrainage.objects.latest('debut')
    except PeriodeParrainage.DoesNotExist:
        return Response({"detail": "Aucune période de parrainage trouvée."}, status=status.HTTP_404_NOT_FOUND)

    # Vérifier si la période actuelle n'est pas dépassée
    now = make_aware(datetime.now())  # Assurez-vous que la date est aware (prend en compte le fuseau horaire)
    
    if periode.debut > now:  # Si la période n'est pas encore commencée
        return Response(
            {"detail": "Vous ne pouvez pas redéfinir les dates tant que la période de parrainage actuelle n'est pas expirée."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Si la période est déjà passée, on permet la modification
    new_debut = request.data.get('debut')
    new_fin = request.data.get('fin')

    # Mettre à jour les dates
    periode.debut = new_debut
    periode.fin = new_fin
    periode.save()

    return Response({"detail": "Période de parrainage mise à jour avec succès."}, status=status.HTTP_200_OK)


# verification de l'existence du numero electeur dans la table electeur
@api_view(['GET'])
def verifier_electeur(request, numero_electeur):
    """ Vérifie si un électeur existe avec ce numero_electeur. """
    try:
        electeur = Electeur.objects.get(numero_electeur=numero_electeur)
        return Response({
            'exists': True,
            'electeur_id': electeur.id,
            'nom': electeur.nom,
            'prenom': electeur.prenom,
            'numero_electeur': electeur.numero_electeur,  # Ajoutez ceci
            'bureau_vote': electeur.bureau_vote,         # Ajoutez ceci
            'cin': electeur.cin,
            'lieu_naissance': electeur.lieu_naissance
        })
    except Electeur.DoesNotExist:
        return Response({'exists': False}, status=404)
    

#pour ajouter un candidat après avoir verifier si son numero electeur existait dans la table electeur
@api_view(['POST'])
def ajouter_candidat(request):
    """ Ajoute un candidat après vérification de l'électeur """
    numero_electeur = request.data.get('electeur')
    
    try:
        electeur = Electeur.objects.get(numero_electeur=numero_electeur)
    except Electeur.DoesNotExist:
        return Response({'error': 'Électeur non trouvé'}, status=status.HTTP_400_BAD_REQUEST)

    # Associer l'électeur et créer le candidat
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
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CandidatListView(APIView):
    def get(self, request):
        try:
            # Utilisez select_related pour optimiser les requêtes SQL
            candidats = Candidat.objects.select_related('electeur').all()
            serializer = CandidatSerializer(candidats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['GET'])
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
            valides=Count('id', filter=Q(electeur__isnull=False))  # ✅ Q est maintenant défini
        )
        .order_by('-total')
    )
    
    return Response(list(results))



# Configuration pour le nombre de parrainages requis
@api_view(['GET'])
def get_total_parrainages_requis(request):
    try:
        config = Configuration.objects.latest('id')
        return Response({'total_parrainages_requis': config.parrainages_requis})
    except Configuration.DoesNotExist:
        return Response({'total_parrainages_requis': 1000})  # Valeur par défaut

# Évolution des parrainages par candidat

@api_view(['GET'])
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




class ParrainageCreateAPIView(generics.CreateAPIView):
    queryset = Parrainage.objects.all()
    serializer_class = ParrainageSerializer

    def create(self, request, *args, **kwargs):
        print("Données reçues:", request.data)  # Debug
        
        try:
            # Validation des données
            electeur_id = request.data.get('electeur')
            candidat_id = request.data.get('candidat')
            
            if not electeur_id or not candidat_id:
                return Response(
                    {"error": "Les champs electeur et candidat sont requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifie si l'électeur existe
            Electeur.objects.get(id=electeur_id)
            
            # Vérifie si le candidat existe
            Candidat.objects.get(id=candidat_id)
            
            # Vérifie si l'électeur a déjà parrainé
            if Parrainage.objects.filter(electeur_id=electeur_id).exists():
                return Response(
                    {"error": "Cet électeur a déjà parrainé un candidat"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Création du parrainage
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
            return Response(
                {"error": "Électeur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Candidat.DoesNotExist:
            return Response(
                {"error": "Candidat non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        





class PeriodeAPI(APIView):
    """Endpoints pour la gestion des périodes"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        """Création d'une nouvelle période"""
        serializer = PeriodeParrainageSerializer(data=request.data)
        
        if serializer.is_valid():
            # Désactive les autres périodes si celle-ci est active
            if serializer.validated_data.get('est_active'):
                PeriodeParrainage.objects.filter(est_active=True).update(est_active=False)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckPeriodAPI(APIView):
    """Vérification de l'état de la période (accessible à tous)"""
    permission_classes = []  # Aucune permission requise

    def get(self, request):
        """Retourne l'état actuel"""
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
    
