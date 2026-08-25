from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from core.views.project_views import serve_deployed_project


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),

    # OpenAPI Schema & Documentation UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Core API endpoints (linked to the layered applications module)
    path('api/', include('core.urls')),

    # Serve Deployed Project Pages
    path('deployed/<str:subdomain>/', serve_deployed_project, name='serve_deployed_project'),
    path('deployed/<str:subdomain>/<str:slug>/', serve_deployed_project, name='serve_deployed_project_slug'),
]
