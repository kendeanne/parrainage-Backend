# middleware.py
from django.http import JsonResponse
from django.utils import timezone
from .models import PeriodeParrainage

class PeriodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = ['/admin/', '/api/login/']  # Routes toujours accessibles

    def __call__(self, request):
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        periode = PeriodeParrainage.objects.filter(est_active=True).first()
        if not periode or not periode.est_en_cours():
            return JsonResponse(
                {"error": "Période de parrainage fermée"}, 
                status=403
            )
        return self.get_response(request)
    



