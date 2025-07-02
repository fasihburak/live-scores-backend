"""
URL configuration for live_scores project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, 
    SpectacularRedocView
)
from rest_framework import routers
from scores.views import view_match
from scores.views import (
    UserViewSet, GroupViewSet, MatchViewSet, TeamViewSet,
    PersonViewSet, InMatchEventViewSet, CompetitionViewSet
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'in-match-events', InMatchEventViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'persons', PersonViewSet)
router.register(r'competitions', CompetitionViewSet)

urlpatterns = [
    path("chat/", include("chat.urls")),
    # path("matches/<uuid:match_id>/", view_match),
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] +\
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +\
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)