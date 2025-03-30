from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ElecteurViewSet, CandidatViewSet, ParrainageViewSet, AgentViewSet
from .views import login_candidat, get_parrainages_candidat, get_evolution_parrainages, get_total_parrainages_requis
from .views import import_electeurs, update_periode_parrainage, verifier_electeur, ajouter_candidat, CandidatListView, monitoring_parrainages
from .views import ParrainageCreateAPIView
from .views import PeriodeAPI, CheckPeriodAPI


router = DefaultRouter()
router.register(r'electeurs', ElecteurViewSet)
router.register(r'candidats', CandidatViewSet)
router.register(r'parrainages', ParrainageViewSet)
router.register(r'agents', AgentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_candidat, name='login_candidat'),
    path('candidats/<int:candidat_id>/parrainages/', get_parrainages_candidat, name='parrainages-candidat'),
    path('import-electeurs/', import_electeurs, name='import-electeurs'),
    path('periode-parrainage/', update_periode_parrainage, name='update_periode_parrainage'),
    path('verifier-electeur/<str:numero_electeur>/', verifier_electeur, name='verifier-electeur'),
    path('ajouter-candidat/', ajouter_candidat, name='ajouter-candidat'),
    path('candidats/', CandidatListView.as_view(), name='candidat-list'),
    path('monitoring-parrainages/', monitoring_parrainages, name='monitoring_parrainages'),
    path('total-parrainages/', get_total_parrainages_requis, name='total_parrainages'),
    path('evolution-parrainages/<int:candidat_id>/', get_evolution_parrainages, name='evolution_parrainages'),
    path('parrainer/', ParrainageCreateAPIView.as_view() , name='create-parrainage'),
    path('periodes/', PeriodeAPI.as_view(), name='manage-period'),
    path('check-period/', CheckPeriodAPI.as_view(), name='check-period'), 
    
  
]



