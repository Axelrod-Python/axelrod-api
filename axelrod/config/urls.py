from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from core.views import StrategyViewSet


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
]

router = DefaultRouter()

routes = {
    'strategies': StrategyViewSet
}

for route, viewset in routes.items():
    router.register(route, viewset, base_name=route)

urlpatterns += router.urls
