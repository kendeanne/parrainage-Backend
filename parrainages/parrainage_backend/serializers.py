from rest_framework import serializers
from .models import Electeur, Candidat, Parrainage, Agent, PeriodeParrainage
from django.contrib.auth.models import User
from django.utils import timezone


# ✅ Serializer pour les électeurs
class ElecteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electeur
        fields = '__all__'




class CandidatSerializer(serializers.ModelSerializer):
    electeur = serializers.PrimaryKeyRelatedField(queryset=Electeur.objects.all())
    
    # Ajoutez ces champs pour exposer nom/prénom de l'électeur
    nom = serializers.CharField(source='electeur.nom', read_only=True)
    prenom = serializers.CharField(source='electeur.prenom', read_only=True)

    # Nouveau champ pour compter le nombre de parrainages
    parrainages = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Candidat
        fields = [
            'id', 
            'electeur', 
            'nom', 
            'prenom', 
            'parti_politique', 
            'email', 
            'telephone', 
            'slogan', 
            'site_web',
            'parrainages',
        ]

    def get_parrainages(self, obj):
        return Parrainage.objects.filter(candidat=obj).count()


# ✅ Serializer pour les parrainages
class ParrainageSerializer(serializers.ModelSerializer):
    electeur = ElecteurSerializer()
    candidat = CandidatSerializer()

    class Meta:
        model = Parrainage
        fields = '__all__'

# ✅ Serializer pour les agents DGE
class AgentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Agent
        fields = '__all__'




class CreateParrainageSerializer(serializers.ModelSerializer):
    electeur_id = serializers.IntegerField(write_only=True)
    candidat_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Parrainage
        fields = ['electeur_id', 'candidat_id']
        
    def validate(self, data):
        # Vérification de l'existence des instances
        try:
            electeur = Electeur.objects.get(id=data['electeur_id'])
            candidat = Candidat.objects.get(id=data['candidat_id'])
        except Electeur.DoesNotExist:
            raise serializers.ValidationError({"electeur_id": "Électeur non trouvé"})
        except Candidat.DoesNotExist:
            raise serializers.ValidationError({"candidat_id": "Candidat non trouvé"})
        
        # Vérification des règles métier
        if Parrainage.objects.filter(electeur=electeur).exists():
            raise serializers.ValidationError({"electeur_id": "Cet électeur a déjà parrainé un candidat"})
            
        if hasattr(electeur, 'candidat'):
            raise serializers.ValidationError({"electeur_id": "Un candidat ne peut pas parrainer un autre candidat"})
            
        # Vérification de la période de parrainage (optionnelle)
        periode = PeriodeParrainage.objects.first()
        if periode and not (periode.debut <= timezone.now() <= periode.fin):
            raise serializers.ValidationError({"non_field_errors": ["La période de parrainage n'est pas ouverte"]})
            
        # Ajout des objets complets aux données validées
        data['electeur'] = electeur
        data['candidat'] = candidat
        
        return data
        
    def create(self, validated_data):
        return Parrainage.objects.create(
            electeur=validated_data['electeur'],
            candidat=validated_data['candidat']
        )
    


class PeriodeParrainageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodeParrainage
        fields = '__all__'

    def validate(self, data):
        if data['date_debut'] >= data['date_fin']:
            raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        return data