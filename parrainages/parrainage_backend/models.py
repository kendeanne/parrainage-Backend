from django.db import models
from django.contrib.auth.models import User  
import random
import string
from django.db import models
from django.utils import timezone

# ✅ Modèle Electeur
class Electeur(models.Model):
    cin = models.CharField(max_length=15, unique=True)
    numero_electeur = models.CharField(max_length=15, unique=True)
    nom = models.CharField(max_length=15)
    prenom = models.CharField(max_length=30)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=40)
    bureau_vote = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])  # Ajout du champ sexe
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"

# ✅ Modèle Candidat (lié à un électeur existant)
class Candidat(models.Model):
    electeur = models.OneToOneField(
        Electeur, 
        on_delete=models.CASCADE, 
        related_name="candidat"
    )
    parti_politique = models.TextField()
    email = models.EmailField(max_length=191, unique=True)
    telephone = models.CharField(max_length=20, unique=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    slogan = models.CharField(max_length=200) 
    site_web = models.CharField(max_length=70)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generer_code()
        super().save(*args, **kwargs)

    def generer_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def __str__(self):
        return f"{self.electeur.nom} {self.electeur.prenom} (Candidat)"

# ✅ Modèle Parrainage
class Parrainage(models.Model):
    electeur = models.OneToOneField(
        Electeur, 
        on_delete=models.CASCADE, 
        related_name="parrainage_electeur"
    )
    candidat = models.ForeignKey(
        Candidat, 
        on_delete=models.CASCADE, 
        related_name="parrainage_candidat"
    )
    date_parrainage = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.electeur.nom} parraine {self.candidat.electeur.nom}"

# ✅ Modèle Agent DGE
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    nom = models.CharField(max_length=15)
    prenom = models.CharField(max_length=30)
    role = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} (Agent DGE)"

class HistoriqueImportation(models.Model):
    user_name = models.CharField(max_length=255)
    user_prenom = models.CharField(max_length=255)
    user_ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f'{self.user_name} - {self.timestamp}'
    




class PeriodeParrainage(models.Model):
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    est_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Période du {self.date_debut} au {self.date_fin}"

    def est_en_cours(self):
        now = timezone.now()
        return self.date_debut <= now <= self.date_fin




class Configuration(models.Model):
    parrainages_requis = models.PositiveIntegerField(default=50000)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parrainages requis: {self.parrainages_requis}"
