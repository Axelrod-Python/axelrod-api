from django.conf import settings
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from api.core.views import (
    MatchViewSet,
    MoranViewSet,
    StrategyViewSet,
    TournamentViewSet,
)


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

router = DefaultRouter()

routes = {
    'matches': MatchViewSet,
    'moran': MoranViewSet,
    'strategies': StrategyViewSet,
    'tournaments': TournamentViewSet,
}

for route, viewset in routes.items():
    router.register(route, viewset, base_name=route)

urlpatterns += router.urls
