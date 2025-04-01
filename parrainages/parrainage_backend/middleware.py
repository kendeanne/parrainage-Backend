# middleware.py
from django.http import JsonResponse
from django.utils import timezone
from .models import PeriodeParrainage

class PeriodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = ['/api/admin/', '/api/login/']  # Routes toujours accessibles

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
    



class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "https://parrainage-frontend-eight.vercel.app/api/"  # Remplacez par votre origine
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response    