from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from core.views import StrategyViewSet


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
]

router = DefaultRouter()
router.register(r'strategies', StrategyViewSet, base_name='strategies')

routes = {
}

for route, viewset in routes.items():
    router.register(route, viewset)

urlpatterns += router.urls
