from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

urlpatterns = [url(r'^api-auth/', include('rest_framework.urls'))]
router = DefaultRouter()

routes = {}

for route, viewset in routes.items():
    router.register(route, viewset)

urlpatterns += router.urls
